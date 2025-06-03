import pandas as pd
import os
import json
import threading
import time
import tempfile
from datetime import datetime, timedelta

class ExcelLogger:
    def __init__(self, log_file_path="data/delivery_log.xlsx"):
        self.log_file_path = log_file_path
        self.lock = threading.Lock()
        self._create_if_missing()

    def _create_if_missing(self):

        if not os.path.exists(self.log_file_path):
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            # Create DataFrame with correct columns and string dtypes for time columns (hardcoded now, later we can use a config)
            # Note: We use pd.Series(dtype="object") to ensure empty columns are created with object dtype
            df = pd.DataFrame({
                "Name": pd.Series(dtype="object"),
                "Phone": pd.Series(dtype="object"),
                "Message": pd.Series(dtype="object"),
                "Message_Sent_Time": pd.Series(dtype="object"),
                "Delivery_Status": pd.Series(dtype="object"),
                "Message_ID": pd.Series(dtype="object"),
                "Last_Updated": pd.Series(dtype="object"),
                "Retry_Count": pd.Series(dtype="Int64"),
                "Next_Retry_Time": pd.Series(dtype="object"),
                "Follow_Up_Status": pd.Series(dtype="object"),
                "Follow_Up_Sent_Time": pd.Series(dtype="object"),
                "Followup_Message": pd.Series(dtype="object"),   
                "Reply_History": pd.Series(dtype="object")
            })
            self._atomic_write(df)

    def _safe_read(self, retries=3, wait=0.5):

        for attempt in range(1, retries + 1):
            try:
                df = pd.read_excel(self.log_file_path, engine="openpyxl")
                return df
            except Exception as e:
                print(f"Error reading Excel file (attempt {attempt}/{retries}): {e}")
                time.sleep(wait)
        return None

    def _atomic_write(self, df: pd.DataFrame):

        temp_fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
        os.close(temp_fd)
        try:
            # Use pandas to_excel to write to temp_path
            df.to_excel(temp_path, index=False)
            # Replace the original file (atomic on most OSes)
            os.replace(temp_path, self.log_file_path)
        except Exception as e:
            print(f"Error writing Excel file atomically: {e}")
            # Cleanup temp file if something went wrong
            try:
                os.remove(temp_path)
            except:
                pass

    def log_message_batch(self, results):
       
        with self.lock:
            self._create_if_missing()
            existing_df = self._safe_read()
            if existing_df is None:
                print("Skipping log_message_batch; log file unreadable.")
                return False

            log_data = []
            for r in results:
                entry = {
                    "Name": r.get("name", ""),
                    "Phone": r.get("phone", ""),
                    "Message": r.get("message", ""),
                    "Message_Sent_Time": r.get("timestamp", ""),
                    "Delivery_Status": r.get("status", "unknown"),
                    "Message_ID": r.get("message_id", ""),
                    "Last_Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Retry_Count": 0,
                    "Next_Retry_Time": "",
                    "Follow_Up_Status": "pending",
                    "Follow_Up_Sent_Time": "",
                    "Followup_Message": "",           # blank for now
                    "Reply_History": json.dumps([]),
                }
                log_data.append(entry)

            new_df = pd.DataFrame(log_data)
            combined = pd.concat([existing_df, new_df], ignore_index=True)
            self._atomic_write(combined)
            return True

    def update_delivery_status(self, message_id, new_status):
        
        with self.lock:
            df = self._safe_read()
            if df is None:
                print("Skipping update_delivery_status; log file unreadable.")
                return False

            if "Message_ID" not in df.columns or "Delivery_Status" not in df.columns:
                return False

            mask = df["Message_ID"] == message_id
            if not mask.any():
                return False

            idx = df[mask].index[-1]
            df.at[idx, "Delivery_Status"] = new_status
            df.at[idx, "Last_Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._atomic_write(df)
            return True

    def get_current_data(self):
        
        df = self._safe_read()
        return df if df is not None else pd.DataFrame()

    def update_reply_status(self, message_id, reply_text, reply_timestamp):
      
        with self.lock:
            df = self._safe_read()
            if df is None:
                print("Skipping update_reply_status; log file unreadable.")
                return False

            if "Message_ID" not in df.columns or "Reply_History" not in df.columns:
                return False

            mask = df["Message_ID"] == message_id
            if not mask.any():
                return False

            idx = df[mask].index[-1]
            history = df.at[idx, "Reply_History"]
            try:
                hist_list = json.loads(history) if (pd.notna(history) and history != "") else []
            except:
                hist_list = []

            hist_list.append({"text": reply_text, "timestamp": reply_timestamp})
            df.at[idx, "Reply_History"] = json.dumps(hist_list)
            df.at[idx, "Delivery_Status"] = "success"
            df.at[idx, "Follow_Up_Status"] = "not_required"
            df.at[idx, "Last_Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._atomic_write(df)
            return True

    def retry_failed_messages(self, api_client, current_time):
   
        with self.lock:
            df = self._safe_read()
            if df is None:
                print("Skipping retry_failed_messages; log file unreadable.")
                return

            if not {"Delivery_Status", "Retry_Count", "Next_Retry_Time"}.issubset(df.columns):
                return

            mask = (df["Delivery_Status"] == "failed") & (df["Retry_Count"] < 5)
            for idx, row in df[mask].iterrows():
                nxt_rt = row["Next_Retry_Time"]
                if pd.isna(nxt_rt) or pd.to_datetime(nxt_rt) <= current_time:
                    res = api_client.send_message(row["Phone"], row["Message"])
                    df.at[idx, "Delivery_Status"] = res.get("status", "failed")
                    df.at[idx, "Message_ID"] = res.get("message_id", "")
                    df.at[idx, "Retry_Count"] = row["Retry_Count"] + 1
                    df.at[idx, "Last_Updated"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    nxt_time = current_time + pd.Timedelta(minutes=1)
                    df.at[idx, "Next_Retry_Time"] = nxt_time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Retry {row['Retry_Count'] + 1} for {row['Name']}: {res.get('status')}")

            self._atomic_write(df)

    def send_followups(self, api_client, current_time):
      
        with self.lock:
            df = self._safe_read()
            if df is None:
                print("Skipping send_followups; log file unreadable.")
                return

            required = {"Delivery_Status", "Reply_History", "Follow_Up_Status", "Message_Sent_Time"}
            if not required.issubset(df.columns):
                return

            def no_replies(hist):
                if pd.isna(hist) or hist == "":
                    return True
                try:
                    return len(json.loads(hist)) == 0
                except:
                    return True

            mask = (
                (df["Delivery_Status"] == "sent")
                & df["Reply_History"].apply(no_replies)
                & (df["Follow_Up_Status"] == "pending")
            )

            for idx, row in df[mask].iterrows():
                sent_time = pd.to_datetime(row["Message_Sent_Time"])
                if (current_time - sent_time).total_seconds() >= 10 * 60:
                    name = row["Name"]
                    followup_msg = f"Hi {name}, just a quick follow-up—any questions about our program?"

                    res = api_client.send_message(row["Phone"], followup_msg)
                    df.at[idx, "Follow_Up_Status"] = "sent" if res.get("status") in ("queued", "sent") else "failed"
                    df.at[idx, "Follow_Up_Sent_Time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[idx, "Followup_Message"] = followup_msg
                    df.at[idx, "Last_Updated"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Follow-up sent to {row['Name']}: {res.get('status')}")

            self._atomic_write(df)

    def start_status_monitoring(self, api_client, check_interval=30):
      

        def monitor():
            while True:
                try:
                    df = self._safe_read()
                    if df is None:
                        time.sleep(check_interval)
                        continue

                    current_time = datetime.now()

                    # 1. Update status for queued messages
                    if "Delivery_Status" in df.columns and "Message_ID" in df.columns:
                        queued_mask = df["Delivery_Status"] == "queued"
                        for _, row in df[queued_mask].iterrows():
                            mid = row["Message_ID"]
                            if pd.notna(mid) and mid != "":
                                status = api_client.get_message_status(mid)
                                if status != row["Delivery_Status"]:
                                    self.update_delivery_status(mid, status)

                    # 2. Retry failed messages
                    self.retry_failed_messages(api_client, current_time)

                    # 3. Check for replies (only within 1 hour)
                    if "Delivery_Status" in df.columns and "Message_ID" in df.columns and "Reply_History" in df.columns:
                        sent_mask = df["Delivery_Status"] == "sent"
                        for _, row in df[sent_mask].iterrows():
                            mid = row["Message_ID"]
                            hist = row["Reply_History"]
                            if pd.isna(hist) or hist == "[]":
                                sent_time = pd.to_datetime(row["Message_Sent_Time"])
                                if (current_time - sent_time) <= timedelta(hours=1):
                                    reply_data = api_client.get_reply(mid)
                                    if reply_data.get("reply"):
                                        self.update_reply_status(mid, reply_data["reply"], reply_data["timestamp"])

                    # 4. Send follow-ups (after 10 minutes)
                    self.send_followups(api_client, current_time)

                except Exception as e:
                    print(f"Error in status monitoring: {e}")

                time.sleep(check_interval)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

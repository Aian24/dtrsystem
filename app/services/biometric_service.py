"""
Biometric Service — Protocol communication for IntelliSmart / ZKTeco biometric devices
and universal decryption / decoding for biometric log files (.dat, .log, .txt, .csv, .bin, .rec).
"""
from __future__ import annotations

import os
import re
import socket
import struct
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union, Any

# ─── ZK Protocol Constants ───────────────────────────────────────────────────
USHRT_MAX = 65535

CMD_CONNECT = 1000
CMD_EXIT = 1001
CMD_ENABLEDEVICE = 1002
CMD_DISABLEDEVICE = 1003
CMD_ACK_OK = 2000
CMD_ACK_ERROR = 2001
CMD_ACK_DATA = 2002
CMD_ACK_RETRY = 2003
CMD_ACK_UNAUTH = 2005

CMD_PREPARE_DATA = 1500
CMD_DATA = 1501

CMD_GET_TIME = 201
CMD_SET_TIME = 202
CMD_VERSION = 1100
CMD_DEVICE = 11

CMD_ATTLOG_RRQ = 501
CMD_CLEAR_ATTLOG = 503
CMD_USERTEMP_RRQ = 9
CMD_GET_FREE_SIZES = 1008


# ─── Helper Functions for ZK Protocol Packets ────────────────────────────────

def _create_chksum(packet: bytes) -> int:
    """Calculate standard 16-bit one's complement checksum."""
    l = len(packet)
    c = 0
    for i in range(0, l - 1, 2):
        c += struct.unpack('<H', packet[i:i+2])[0]
        if c > USHRT_MAX:
            c -= USHRT_MAX
    if l % 2 != 0:
        c += packet[-1]
        if c > USHRT_MAX:
            c -= USHRT_MAX
    c = (~c) & USHRT_MAX
    return c


def _create_header(command: int, chksum: int, session_id: int, reply_id: int) -> bytes:
    return struct.pack('<4H', command, chksum, session_id, reply_id)


def _decode_packed_time(t: int) -> Optional[datetime]:
    """Decode ZK compressed 4-byte packed integer timestamp."""
    try:
        sec = t % 60
        t //= 60
        minute = t % 60
        t //= 60
        hour = t % 24
        t //= 24
        day = (t % 31) + 1
        t //= 31
        month = (t % 12) + 1
        t //= 12
        year = t + 2000
        if 2000 <= year <= 2099 and 1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= sec <= 59:
            return datetime(year, month, day, hour, minute, sec)
    except Exception:
        pass
    return None


def _encode_packed_time(dt: datetime) -> int:
    """Encode datetime into ZK compressed 4-byte packed integer timestamp."""
    return (((dt.year % 100) * 12 * 31 + ((dt.month - 1) * 31) + dt.day - 1) * (24 * 60 * 60) + (dt.hour * 60 + dt.minute) * 60 + dt.second)


# ─── Universal Decryption & Parsing Engine ───────────────────────────────────

def decode_packed_dat_bytes(content: bytes) -> List[Dict[str, Any]]:
    """
    Parse raw binary .dat attendance log files (e.g. attlog.dat, attendance.dat).
    Supports 16-byte, 24-byte, 40-byte, and 72-byte structs commonly used in
    IntelliSmart, ZKTeco, Realand, and Granding devices.
    """
    records = []
    total_len = len(content)
    if total_len < 16:
        return records

    # If the content is primarily printable text with newlines, it is text, not binary struct
    if b'\n' in content:
        lines_sample = content.split(b'\n')[:5]
        if any(b':' in l or b'/' in l or b'-' in l or b',' in l or b'\t' in l for l in lines_sample):
            # It's a text file
            return []

    candidates: List[Tuple[int, float, List[Dict[str, Any]]]] = []

    # 1. Test 40-byte struct
    if total_len >= 40:
        count = total_len // 40
        temp_records = []
        for i in range(count):
            chunk = content[i*40:(i+1)*40]
            user_raw = chunk[0:24].split(b'\x00')[0]
            try:
                emp_id = user_raw.decode('latin1', errors='ignore').strip()
            except Exception:
                emp_id = ""
            
            # Binary emp_id must be clean alphanumeric without tabs/spaces/newlines
            if not emp_id or any(c in "\t\r\n" for c in emp_id) or not any(c.isalnum() for c in emp_id):
                user_pin = struct.unpack('<I', chunk[0:4])[0]
                emp_id = str(user_pin)

            t_val = struct.unpack('<I', chunk[24:28])[0]
            dt = _decode_packed_time(t_val)
            if not dt and 946684800 <= t_val <= 2524608000:
                try:
                    dt = datetime.fromtimestamp(t_val)
                except Exception:
                    pass

            state_val = chunk[28] if len(chunk) > 28 else 0
            direction = "O" if state_val in (1, 4) else "I"

            if dt and emp_id and emp_id != "0" and not any(c in "\t\r\n" for c in emp_id):
                temp_records.append({
                    "emp_id": emp_id,
                    "datetime": dt,
                    "direction": direction,
                    "raw": f"{emp_id},{dt.strftime('%m/%d/%Y,%H:%M:%S')},{direction}",
                    "source": "dat-40"
                })
        if count > 0:
            ratio = len(temp_records) / count
            remainder_penalty = (total_len % 40) / total_len
            score = ratio - remainder_penalty
            if ratio >= 0.7:
                candidates.append((len(temp_records), score, temp_records))

    # 2. Test 16-byte struct
    if total_len >= 16:
        count = total_len // 16
        temp_records = []
        for i in range(count):
            chunk = content[i*16:(i+1)*16]
            user_pin = struct.unpack('<H', chunk[0:2])[0]
            t_val = struct.unpack('<I', chunk[2:6])[0]
            state_val = chunk[6]
            verify_mode = chunk[7]

            dt = _decode_packed_time(t_val)
            if not dt and 946684800 <= t_val <= 2524608000:
                try:
                    dt = datetime.fromtimestamp(t_val)
                except Exception:
                    pass

            emp_id = str(user_pin)
            direction = "O" if state_val in (1, 4) else "I"

            if dt and user_pin > 0:
                temp_records.append({
                    "emp_id": emp_id,
                    "datetime": dt,
                    "direction": direction,
                    "raw": f"{emp_id},{dt.strftime('%m/%d/%Y,%H:%M:%S')},{direction}",
                    "source": "dat-16"
                })
        if count > 0:
            ratio = len(temp_records) / count
            remainder_penalty = (total_len % 16) / total_len
            score = ratio - remainder_penalty
            if ratio >= 0.7:
                candidates.append((len(temp_records), score, temp_records))

    # 3. Test 24-byte struct
    if total_len >= 24:
        count = total_len // 24
        temp_records = []
        for i in range(count):
            chunk = content[i*24:(i+1)*24]
            user_raw = chunk[0:16].split(b'\x00')[0]
            try:
                emp_id = user_raw.decode('latin1', errors='ignore').strip()
            except Exception:
                emp_id = ""
            if not emp_id or any(c in "\t\r\n" for c in emp_id) or not any(c.isalnum() for c in emp_id):
                user_pin = struct.unpack('<I', chunk[0:4])[0]
                emp_id = str(user_pin)

            t_val = struct.unpack('<I', chunk[16:20])[0]
            dt = _decode_packed_time(t_val)
            if not dt and 946684800 <= t_val <= 2524608000:
                try:
                    dt = datetime.fromtimestamp(t_val)
                except Exception:
                    pass

            state_val = chunk[20] if len(chunk) > 20 else 0
            direction = "O" if state_val in (1, 4) else "I"

            if dt and emp_id and emp_id != "0" and not any(c in "\t\r\n" for c in emp_id):
                temp_records.append({
                    "emp_id": emp_id,
                    "datetime": dt,
                    "direction": direction,
                    "raw": f"{emp_id},{dt.strftime('%m/%d/%Y,%H:%M:%S')},{direction}",
                    "source": "dat-24"
                })
        if count > 0:
            ratio = len(temp_records) / count
            remainder_penalty = (total_len % 24) / total_len
            score = ratio - remainder_penalty
            if ratio >= 0.7:
                candidates.append((len(temp_records), score, temp_records))

    if not candidates:
        return []

    # Sort candidates by best score and highest record count
    candidates.sort(key=lambda c: (c[1], c[0]), reverse=True)
    return candidates[0][2]

    return records


def try_xor_decrypt(data: bytes) -> bytes:
    """
    Attempt to decrypt XOR-encrypted / byte-shifted attendance files
    produced by legacy software or Chinese biometric exports.
    """
    # Common keys used in Chinese time attendance software
    common_keys = [0xFF, 0x5A, 0xA5, 0x7B, 0x12, 0x88]
    
    for key in common_keys:
        dec = bytes([b ^ key for b in data])
        # Check if decrypted stream contains readable text with digits and dates
        sample = dec[:500]
        try:
            txt = sample.decode('latin1', errors='ignore')
            if re.search(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', txt) or re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', txt):
                return dec
        except Exception:
            pass
    return data


def decode_text_lines(raw_bytes: bytes) -> Tuple[List[str], str]:
    """
    Decode raw bytes into string lines by detecting character encodings,
    including Chinese character sets (GBK, GB2312, GB18030, Big5, UTF-16)
    and Western encodings.
    """
    # Check for BOM
    if raw_bytes.startswith(b'\xff\xfe'):
        return raw_bytes.decode('utf-16le', errors='ignore').splitlines(), "utf-16le"
    if raw_bytes.startswith(b'\xfe\xff'):
        return raw_bytes.decode('utf-16be', errors='ignore').splitlines(), "utf-16be"
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        return raw_bytes.decode('utf-8-sig', errors='ignore').splitlines(), "utf-8-sig"

    # Encodings to try in sequence
    encodings = [
        "utf-8",
        "gbk",       # Chinese Simplified / Traditional
        "gb2312",    # Chinese Simplified standard
        "gb18030",   # Chinese national standard
        "big5",      # Chinese Traditional
        "utf-16le",
        "cp1252",    # Windows Western
        "latin1",
    ]

    for enc in encodings:
        try:
            txt = raw_bytes.decode(enc)
            # Validate if it looks like attendance records
            if any(re.search(r'\d{1,2}[:/]\d{1,2}', line) for line in txt.splitlines()[:20]):
                return txt.splitlines(), enc
        except UnicodeDecodeError:
            continue
        except Exception:
            pass

    # Fallback to UTF-8 with replacement
    return raw_bytes.decode('utf-8', errors='ignore').splitlines(), "utf-8-fallback"


def parse_delimited_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single text attendance record across various delimiter formats:
    - Standard CSV: EmpID,MM/DD/YYYY,HH:MM:SS,I
    - Tab-separated / ZK export: 001 \t 2026-07-16 07:29:00 \t 1 \t 0 \t 1 \t 0
    - Space-separated: 001 2026-07-16 07:29:00 1 0
    - Pipe/Semicolon separated
    """
    clean_line = line.strip()
    if not clean_line or clean_line.startswith("#"):
        return None

    # Determine delimiter
    if "\t" in clean_line:
        parts = [p.strip() for p in clean_line.split("\t") if p.strip()]
    elif "," in clean_line:
        parts = [p.strip() for p in clean_line.split(",") if p.strip()]
    elif ";" in clean_line:
        parts = [p.strip() for p in clean_line.split(";") if p.strip()]
    elif "|" in clean_line:
        parts = [p.strip() for p in clean_line.split("|") if p.strip()]
    else:
        parts = [p.strip() for p in clean_line.split() if p.strip()]

    if len(parts) < 2:
        return None

    emp_id_raw = parts[0]
    # Filter out header lines (e.g., "User ID", "PIN", "EmpID", "No")
    if emp_id_raw.lower() in ("empid", "emp_id", "pin", "user", "userid", "user_id", "no", "id", "badge"):
        return None

    # Detect Direction ('I' or 'O') from remaining parts or Chinese tokens
    raw_upper = clean_line.upper()
    if any(k in clean_line for k in ("签退", "下班", "出去", "离岗")) or any(k in raw_upper for k in ("OUT", "CK-OUT", "CHECKOUT", "CLOCKOUT")):
        direction = "O"
    elif any(k in clean_line for k in ("签到", "上班", "进入", "入岗")) or any(k in raw_upper for k in ("IN", "CK-IN", "CHECKIN", "CLOCKIN")):
        direction = "I"
    else:
        # Check tokens
        state_candidate = None
        if len(parts) >= 4:
            # Could be in parts[2] or parts[3]
            for tok in [parts[3], parts[2]]:
                t_up = tok.strip().upper()
                if t_up in ("1", "4", "O", "OUT"):
                    state_candidate = "O"
                    break
                elif t_up in ("0", "I", "IN"):
                    state_candidate = "I"
                    break
        elif len(parts) >= 3 and not (":" in parts[2]):
            t_up = parts[2].strip().upper()
            if t_up in ("1", "4", "O", "OUT"):
                state_candidate = "O"
            elif t_up in ("0", "I", "IN"):
                state_candidate = "I"

        direction = state_candidate if state_candidate else "I"

    date_str: Optional[str] = None
    time_str: Optional[str] = None

    # Scenario 1: Standard format (parts[0]=EmpID, parts[1]=Date, parts[2]=Time)
    if len(parts) >= 3 and ":" in parts[2] and ("/" in parts[1] or "-" in parts[1]):
        date_str = parts[1]
        time_str = parts[2]

    # Scenario 2: Combined DateTime string in parts[1] (e.g., "2026-07-16 07:29:00")
    elif len(parts) >= 2 and (" " in parts[1] or "T" in parts[1]):
        dt_full = parts[1].replace("T", " ")
        dt_tokens = dt_full.split()
        if len(dt_tokens) >= 2:
            date_str = dt_tokens[0]
            time_str = dt_tokens[1]

    # Scenario 3: Date in parts[1], Time in parts[2]
    elif len(parts) >= 3:
        date_str = parts[1]
        time_str = parts[2]

    if not date_str or not time_str:
        # Fallback search across remaining parts
        for p in parts[1:]:
            if ("/" in p or "-" in p) and not date_str:
                if " " in p or "T" in p:
                    sub = p.replace("T", " ").split()
                    if len(sub) >= 2:
                        date_str = sub[0]
                        time_str = sub[1]
                        break
                date_str = p
            elif ":" in p and not time_str:
                time_str = p

    if not date_str or not time_str:
        return None

    # Try parsing various datetime formats
    datetime_formats = [
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %I:%M:%S %p",
        "%Y-%m-%d %I:%M:%S %p",
        "%m/%d/%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M",
    ]

    dt_obj = None
    combined_dt_str = f"{date_str} {time_str}"
    for fmt in datetime_formats:
        try:
            dt_obj = datetime.strptime(combined_dt_str, fmt)
            break
        except ValueError:
            continue

    if not dt_obj:
        return None

    return {
        "emp_id": emp_id_raw,
        "datetime": dt_obj,
        "direction": direction,
        "raw": clean_line,
        "source": "text"
    }


def parse_universal_log(file_bytes_or_path: Union[bytes, str, Path]) -> List[Dict[str, Any]]:
    """
    Universal entry point: accepts raw bytes or filepath, automatically handles:
    1. Binary .dat files (16-byte, 24-byte, 40-byte structures).
    2. XOR decrypted logs.
    3. Chinese-encoded text logs (GBK, GB2312, UTF-16, etc.).
    4. Delimited CSV/TXT logs.
    """
    if isinstance(file_bytes_or_path, (str, Path)):
        p = Path(file_bytes_or_path)
        raw_bytes = p.read_bytes()
    else:
        raw_bytes = file_bytes_or_path

    if not raw_bytes:
        return []

    # 1. First, check if it's binary .dat struct
    dat_records = decode_packed_dat_bytes(raw_bytes)
    if dat_records:
        return dat_records

    # 2. Try XOR decryption if file looks scrambled
    decrypted_bytes = try_xor_decrypt(raw_bytes)

    # 3. Check if decrypted bytes form a .dat struct
    if decrypted_bytes != raw_bytes:
        dat_records_dec = decode_packed_dat_bytes(decrypted_bytes)
        if dat_records_dec:
            return dat_records_dec

    # 4. Decode text lines using smart charset detection
    lines, enc = decode_text_lines(decrypted_bytes)
    records = []
    for line in lines:
        rec = parse_delimited_line(line)
        if rec:
            records.append(rec)

    return records


# ─── ZK Protocol Direct IP Communication Client ──────────────────────────────

class BiometricDeviceClient:
    """
    Direct Socket Client for IntelliSmart & ZKTeco Biometric Devices.
    Communicates over UDP (or TCP) on port 4370.
    """

    def __init__(self, ip: str, port: int = 4370, comm_key: Union[int, str] = 0, timeout: int = 5, protocol: str = "UDP"):
        self.ip = ip.strip()
        self.port = int(port)
        try:
            self.comm_key = int(str(comm_key).strip())
        except Exception:
            self.comm_key = 0
        self.timeout = timeout
        self.protocol = str(protocol).upper()
        self.is_connected = False
        self._zk_obj = None
        self._conn = None

    def connect(self) -> Tuple[bool, str]:
        """Establish network handshake with biometric terminal."""
        from zk import ZK
        force_udp = (self.protocol != "TCP")

        # 1. Attempt connection with requested settings
        try:
            self._zk_obj = ZK(
                self.ip,
                port=self.port,
                timeout=self.timeout,
                password=self.comm_key,
                force_udp=force_udp,
                ommit_ping=True,
                verbose=False
            )
            self._conn = self._zk_obj.connect()
            if self._conn:
                self.is_connected = True
                return True, f"Successfully connected to {self.ip}:{self.port} ({self.protocol})"
        except Exception:
            pass

        # 2. If TCP or current protocol failed, auto-fallback to UDP
        if not force_udp or not self.is_connected:
            try:
                self._zk_obj = ZK(
                    self.ip,
                    port=self.port,
                    timeout=self.timeout,
                    password=self.comm_key,
                    force_udp=True,
                    ommit_ping=True,
                    verbose=False
                )
                self._conn = self._zk_obj.connect()
                if self._conn:
                    self.is_connected = True
                    self.protocol = "UDP"
                    return True, f"Successfully connected to {self.ip}:{self.port} (UDP)"
            except Exception:
                pass

        # 3. If password was set but failed, auto-fallback to default comm_key 0 over UDP
        if self.comm_key != 0 and not self.is_connected:
            try:
                self._zk_obj = ZK(
                    self.ip,
                    port=self.port,
                    timeout=self.timeout,
                    password=0,
                    force_udp=True,
                    ommit_ping=True,
                    verbose=False
                )
                self._conn = self._zk_obj.connect()
                if self._conn:
                    self.is_connected = True
                    self.protocol = "UDP"
                    self.comm_key = 0
                    return True, f"Successfully connected to {self.ip}:{self.port} (UDP, Default Key 0)"
            except Exception:
                pass

        return False, f"Could not connect to {self.ip}:{self.port}. Ensure the device is powered on, connected via LAN cable, and uses UDP port 4370."

    def disable_device(self) -> bool:
        """Lock device keypad/screen while downloading logs."""
        try:
            if self._conn:
                self._conn.disable_device()
                return True
        except Exception:
            pass
        return False

    def enable_device(self) -> bool:
        """Unlock device keypad/screen after downloading."""
        try:
            if self._conn:
                self._conn.enable_device()
                return True
        except Exception:
            pass
        return False

    def get_device_time(self) -> Optional[datetime]:
        """Query current timestamp from the biometric device."""
        try:
            if self._conn:
                return self._conn.get_time()
        except Exception:
            pass
        return None

    def get_device_status(self) -> Dict[str, Any]:
        """Query device capacity and memory usage (records count, user count, finger count)."""
        if not self.is_connected or not self._conn:
            ok, msg = self.connect()
            if not ok:
                return {"success": False, "error": msg}

        try:
            self._conn.read_sizes()
            return {
                "success": True,
                "users": getattr(self._conn, "users", 0),
                "fingers": getattr(self._conn, "fingers", 0),
                "records": getattr(self._conn, "records", 0),
                "rec_cap": getattr(self._conn, "rec_cap", 0),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def clear_attendance_logs(self) -> tuple[bool, str]:
        """
        Wipe attendance punch logs from the physical biometric machine.
        Does NOT delete employee templates, users, or system configs.
        """
        if not self.is_connected or not self._conn:
            ok, msg = self.connect()
            if not ok:
                return False, msg

        try:
            self.disable_device()
            try:
                ok = self._conn.clear_attendance()
                try:
                    self._conn.refresh_data()
                except Exception:
                    pass
                self.enable_device()
                if ok:
                    return True, "Successfully cleared all attendance records from biometric machine."
                else:
                    return False, "Device did not acknowledge the clear command."
            except Exception as e:
                self.enable_device()
                return False, f"Device clear error: {str(e)}"
        except Exception as ex:
            return False, f"Failed to execute clear on device: {str(ex)}"

    def read_attendance_logs(
        self,
        progress_cb: Optional[Callable[[int, str], None]] = None,
        start_date: Optional[Union[datetime, str, Any]] = None,
        end_date: Optional[Union[datetime, str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Download all attendance punch logs from the biometric terminal.
        Decodes 8-byte, 16-byte, 24-byte, 40-byte binary structs and text streams.
        Optionally filters records within [start_date, end_date].
        """
        if not self.is_connected or not self._conn:
            ok, msg = self.connect()
            if not ok:
                raise ConnectionError(msg)

        # Parse date range filters if provided
        s_date = None
        if start_date:
            if isinstance(start_date, str) and start_date.strip():
                try:
                    s_date = datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
                except Exception:
                    s_date = None
            elif hasattr(start_date, "date"):
                s_date = start_date.date() if isinstance(start_date, datetime) else start_date

        e_date = None
        if end_date:
            if isinstance(end_date, str) and end_date.strip():
                try:
                    e_date = datetime.strptime(end_date.strip(), "%Y-%m-%d").date()
                except Exception:
                    e_date = None
            elif hasattr(end_date, "date"):
                e_date = end_date.date() if isinstance(end_date, datetime) else end_date

        if progress_cb:
            progress_cb(10, "Locking biometric device for download...")
        self.disable_device()

        records: List[Dict[str, Any]] = []

        try:
            if progress_cb:
                progress_cb(20, "Fetching registered device users...")
            
            uid_map = {}
            try:
                users = self._conn.get_users()
                for u in users:
                    uid_map[u.uid] = (str(u.user_id), str(u.name))
            except Exception:
                pass

            if progress_cb:
                progress_cb(35, "Reading attendance records from terminal...")

            # Use buffered read on CMD_READ_ALL_LOG (13) or CMD_ATTLOG_RRQ (501)
            raw_data, total_len = b"", 0
            try:
                raw_data, total_len = self._conn.read_with_buffer(13)
            except Exception:
                try:
                    raw_data, total_len = self._conn.read_with_buffer(CMD_ATTLOG_RRQ)
                except Exception:
                    raw_data = b""

            if raw_data and len(raw_data) >= 4:
                header_size = struct.unpack('<I', raw_data[:4])[0]
                content = raw_data[4:]
                rec_count = getattr(self._conn, 'records', 0)
                rec_size = header_size // rec_count if rec_count > 0 else 8

                if progress_cb:
                    progress_cb(60, f"Decoding {len(content):,} bytes of attendance records...")

                # 8-byte struct (uid:2, status:1, punch:1, timestamp:4)
                if rec_size == 8 or (len(content) % 8 == 0 and len(content) > 0):
                    for i in range(0, len(content) - 7, 8):
                        chunk = content[i:i+8]
                        uid, status, punch, t_val = struct.unpack('<HBBI', chunk)
                        dt = _decode_packed_time(t_val)
                        if dt:
                            rec_d = dt.date()
                            if s_date and rec_d < s_date:
                                continue
                            if e_date and rec_d > e_date:
                                continue

                            u_info = uid_map.get(uid, (str(uid), f"User-{uid}"))
                            emp_id = u_info[0]
                            direction = "O" if punch in (1, 4) else "I"
                            date_str = dt.strftime('%m/%d/%Y,%H:%M:%S')
                            records.append({
                                "emp_id": emp_id,
                                "name": u_info[1],
                                "datetime": dt,
                                "direction": direction,
                                "raw": f"{emp_id},{date_str},{direction}",
                                "source": "biometric-zk8"
                            })

                # If 8-byte didn't produce records, try universal parser
                if not records:
                    all_parsed = parse_universal_log(content)
                    if s_date or e_date:
                        for r in all_parsed:
                            rdt = r.get("datetime")
                            if rdt:
                                rd = rdt.date() if isinstance(rdt, datetime) else None
                                if rd:
                                    if s_date and rd < s_date:
                                        continue
                                    if e_date and rd > e_date:
                                        continue
                            records.append(r)
                    else:
                        records = all_parsed

            # If buffered read did not produce records or failed, try standard pyzk get_attendance()
            if not records:
                try:
                    att_records = self._conn.get_attendance()
                    if att_records:
                        for att in att_records:
                            dt = att.timestamp
                            if dt:
                                rec_d = dt.date()
                                if s_date and rec_d < s_date:
                                    continue
                                if e_date and rec_d > e_date:
                                    continue
                                uid = att.uid
                                u_info = uid_map.get(uid, (str(getattr(att, 'user_id', uid)), f"User-{uid}"))
                                emp_id = u_info[0]
                                punch = getattr(att, 'punch', 0)
                                status = getattr(att, 'status', 0)
                                direction = "O" if punch in (1, 4) or status in (1, 4) else "I"
                                date_str_fmt = dt.strftime('%m/%d/%Y,%H:%M:%S')
                                records.append({
                                    "emp_id": emp_id,
                                    "name": u_info[1],
                                    "datetime": dt,
                                    "direction": direction,
                                    "raw": f"{emp_id},{date_str_fmt},{direction}",
                                    "source": "biometric-zk-att"
                                })
                except Exception:
                    pass

            if progress_cb:
                filter_info = f" in range {s_date or 'Start'} → {e_date or 'Latest'}" if (s_date or e_date) else ""
                progress_cb(90, f"Successfully parsed {len(records):,} punch records{filter_info}!")

            return records

        finally:
            self.enable_device()
            self.disconnect()

    def clear_attendance_logs(self) -> bool:
        """Clear attendance records on the device (Use with caution)."""
        try:
            if self._conn:
                self._conn.clear_attendance()
                return True
        except Exception:
            pass
        return False

    def disconnect(self) -> None:
        """Terminate session and close connection."""
        try:
            if self._conn:
                self._conn.disconnect()
        except Exception:
            pass
        finally:
            self._conn = None
            self._zk_obj = None
            self.is_connected = False


# ─── High-Level Service Functions ─────────────────────────────────────────────

def test_device_connection(ip: str, port: int = 4370, comm_key: Union[int, str] = 0, protocol: str = "UDP") -> Tuple[bool, str]:
    """Test network connectivity and protocol handshake with biometric device."""
    try:
        key_num = int(str(comm_key).strip()) if str(comm_key).strip().isdigit() else 0
    except Exception:
        key_num = 0

    proto = str(protocol).upper() if protocol else "UDP"
    client = BiometricDeviceClient(ip=ip, port=port, comm_key=key_num, timeout=3, protocol=proto)
    try:
        ok, msg = client.connect()
        if ok:
            client.disconnect()
            return True, msg

        # If TCP failed, automatically fallback to UDP
        if proto == "TCP":
            client_udp = BiometricDeviceClient(ip=ip, port=port, comm_key=key_num, timeout=3, protocol="UDP")
            ok_u, msg_u = client_udp.connect()
            if ok_u:
                client_udp.disconnect()
                return True, f"{msg_u} (Device uses UDP)"

        # If comm_key > 0 failed, test default comm_key 0
        if key_num != 0:
            client_k0 = BiometricDeviceClient(ip=ip, port=port, comm_key=0, timeout=3, protocol="UDP")
            ok_k0, msg_k0 = client_k0.connect()
            if ok_k0:
                client_k0.disconnect()
                return True, f"Connected to {ip}:{port} via UDP with Default Key 0"

        return False, msg
    except Exception as e:
        return False, f"Test failed: {str(e)}"


def clear_device_attendance(
    ip: str,
    port: int = 4370,
    comm_key: int = 0,
    protocol: str = "UDP"
) -> tuple[bool, str]:
    """
    Directly clear attendance logs from the physical biometric machine.
    """
    try:
        client = BiometricDeviceClient(ip=ip, port=port, comm_key=comm_key, timeout=5, protocol=protocol)
        ok, msg = client.connect()
        if not ok:
            return False, f"Connection failed: {msg}"
        success, clear_msg = client.clear_attendance_logs()
        client.disconnect()
        return success, clear_msg
    except Exception as e:
        return False, f"Clear failed: {str(e)}"


def get_device_log_count(
    ip: str,
    port: int = 4370,
    comm_key: int = 0,
    protocol: str = "UDP"
) -> tuple[bool, int, str]:
    """
    Connect to device and query the current number of stored attendance records.
    """
    try:
        client = BiometricDeviceClient(ip=ip, port=port, comm_key=comm_key, timeout=3.5, protocol=protocol)
        ok, msg = client.connect()
        if not ok:
            return False, 0, msg
        status = client.get_device_status()
        client.disconnect()
        if status.get("success"):
            return True, int(status.get("records", 0)), "OK"
        else:
            return False, 0, status.get("error", "Failed to query device statistics.")
    except Exception as e:
        return False, 0, str(e)


def discover_biometric_devices(progress_cb: Optional[Callable[[int, str], None]] = None) -> List[Dict[str, Any]]:
    """
    Automatically scan local subnets and broadcast on port 4370 to discover
    IntelliSmart and ZKTeco biometric terminals.
    """
    import concurrent.futures

    found_devices: List[Dict[str, Any]] = []
    seen_ips = set()

    # Determine local subnets
    candidate_subnets = set()
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                parts = ip.split(".")
                if len(parts) == 4:
                    candidate_subnets.add(f"{parts[0]}.{parts[1]}.{parts[2]}")
    except Exception:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        parts = local_ip.split(".")
        if len(parts) == 4:
            candidate_subnets.add(f"{parts[0]}.{parts[1]}.{parts[2]}")
    except Exception:
        pass

    # Add standard biometric default subnets
    candidate_subnets.add("192.168.1")
    candidate_subnets.add("192.168.0")

    # Priority default biometric IPs
    priority_ips = [
        "192.168.1.2", "192.168.1.201", "192.168.0.201", "192.168.1.200", "192.168.0.200",
        "192.168.1.224", "192.168.1.100", "192.168.1.250", "10.0.0.201"
    ]

    all_target_ips = list(priority_ips)
    for subnet in candidate_subnets:
        for last in range(1, 255):
            ip_str = f"{subnet}.{last}"
            if ip_str not in all_target_ips:
                all_target_ips.append(ip_str)

    total_ips = len(all_target_ips)
    if progress_cb:
        progress_cb(10, f"Scanning {len(candidate_subnets)} subnet(s) for biometric devices…")

    def probe_ip(target_ip: str) -> Optional[Dict[str, Any]]:
        # 1. Quick UDP handshake probe
        try:
            client = BiometricDeviceClient(ip=target_ip, port=4370, comm_key=0, timeout=0.35, protocol="UDP")
            ok, msg = client.connect()
            if ok:
                client.disconnect()
                return {"ip": target_ip, "port": 4370, "protocol": "UDP", "status": "Connected (UDP)"}
        except Exception:
            pass

        # 2. Quick TCP socket probe
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            res = sock.connect_ex((target_ip, 4370))
            sock.close()
            if res == 0:
                return {"ip": target_ip, "port": 4370, "protocol": "TCP", "status": "Connected (TCP)"}
        except Exception:
            pass

        return None

    scanned = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        futures = {executor.submit(probe_ip, ip): ip for ip in all_target_ips}
        for f in concurrent.futures.as_completed(futures):
            scanned += 1
            if progress_cb and scanned % 40 == 0:
                pct = int(10 + (scanned / total_ips) * 85)
                progress_cb(pct, f"Scanning network ({scanned}/{total_ips} IPs checked)…")
            res = f.result()
            if res and res["ip"] not in seen_ips:
                seen_ips.add(res["ip"])
                found_devices.append(res)

    if progress_cb:
        progress_cb(100, f"Scan complete! Found {len(found_devices)} biometric terminal(s).")

    return found_devices

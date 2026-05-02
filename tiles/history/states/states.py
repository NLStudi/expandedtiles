import os
import re
import shutil

MOD_PATH = r"C:\Users\Ryan-PC\Documents\Paradox Interactive\Hearts of Iron IV\mod\tiles"

STATES_FOLDER = os.path.join(MOD_PATH, "history", "states")
BACKUP_FOLDER = os.path.join(MOD_PATH, "history", "states_ANT_OWNER_FIX_BACKUP")

NEW_OWNER = "ANT"
DRY_RUN = False

ANTARCTICA_STATE_IDS = {
    982, 983, 984, 986, 987, 989,
    997, 998, 999, 1000, 1001, 1003,
    1005, 1007, 1008, 1009, 1010, 1011,
    1012, 1013, 1014, 1015, 1016, 1017,
    1019, 1020, 1021, 1022, 1023, 1024,
    1029, 1030, 1031, 1032, 1033, 1034,
    1035, 1036, 1037, 1038, 1039, 1040,
    1041, 1042, 1043, 1044, 1045, 1046,
    1047, 1055, 1060, 1061
}

STATE_ID_RE = re.compile(r"\bid\s*=\s*(\d+)")
HISTORY_RE = re.compile(r"history\s*=\s*\{")
OWNER_LINE_RE = re.compile(
    r"^\s*(owner|controller|add_core_of)\s*=\s*\w+\s*$",
    re.MULTILINE
)

def read_text(path):
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        return f.read()

def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def get_state_id(text):
    match = STATE_ID_RE.search(text)
    return int(match.group(1)) if match else None

def backup_file(path):
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    dst = os.path.join(BACKUP_FOLDER, os.path.basename(path))
    counter = 1

    while os.path.exists(dst):
        name, ext = os.path.splitext(os.path.basename(path))
        dst = os.path.join(BACKUP_FOLDER, f"{name}_{counter}{ext}")
        counter += 1

    shutil.copy2(path, dst)

def fix_owner(text):
    text = OWNER_LINE_RE.sub("", text)

    replacement = (
        f"history={{\n"
        f"\t\towner = {NEW_OWNER}\n"
        f"\t\tcontroller = {NEW_OWNER}\n"
        f"\t\tadd_core_of = {NEW_OWNER}"
    )

    return HISTORY_RE.sub(replacement, text, count=1)

def main():
    fixed = 0
    missing_ids = set(ANTARCTICA_STATE_IDS)

    for filename in sorted(os.listdir(STATES_FOLDER)):
        if not filename.lower().endswith(".txt"):
            continue

        path = os.path.join(STATES_FOLDER, filename)
        text = read_text(path)
        state_id = get_state_id(text)

        if state_id not in ANTARCTICA_STATE_IDS:
            continue

        missing_ids.discard(state_id)

        print(f"Setting ANT ownership: ID {state_id} / {filename}")

        if not DRY_RUN:
            backup_file(path)
            write_text(path, fix_owner(text))

        fixed += 1

    print()
    print(f"Done. Fixed {fixed} Antarctica states.")
    print(f"Backups saved to: {BACKUP_FOLDER}")

    if missing_ids:
        print("\nThese listed Antarctica IDs were not found:")
        for state_id in sorted(missing_ids):
            print(f"  {state_id}")

    input("\nPress Enter to close...")

if __name__ == "__main__":
    main()
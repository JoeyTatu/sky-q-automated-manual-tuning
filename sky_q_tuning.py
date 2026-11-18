# sky_q_tuning.py
# Automate the Sky Q Manual Tuning screens using LAN remote-control commands.
#
# Requires Python 3.10+ and a reachable Sky Q box (default 192.168.0.7).
# Usage:
#   python sky_q_tuning.py
#   python sky_q_tuning.py --host 192.168.0.7 --list sky_q_frequencies.txt
#
# Input rows use this format:
#   FREQUENCY POLARISATION STANDARD MODULATION SYMBOL_RATE FEC, CHANNEL_LABEL
#   11224 H DVB-S QPSK 27.5 2/3, 7621
# Blank lines and lines beginning with # are ignored.
#
# Start from live TV. Menu positions and dropdown order match the Sky Q layout
# used when this script was developed. Watch the TV to verify navigation.
# The script can delete saved manual channels if requested at its initial prompt.
# After each scan, the user selects and saves the desired channels on the TV.
# Report the number saved accurately so navigation to the next scan stays aligned.
# The final scan also requires the user to select and save channels on the TV.
#
"""Drive Sky Q manual tuning. Run with --help for options."""
import argparse
from pathlib import Path
import socket
import time

# Sky remote protocol key codes. Digit keys use their ASCII codes.
SELECT, HOME, UP, DOWN, LEFT, RIGHT = 1, 11, 16, 17, 18, 19

# Send each key on a separate TCP connection, followed by a short UI delay.
def send(host, keys):
 for key in keys:
  with socket.create_connection((host,49160),3) as s:
   s.settimeout(3)
   # Echo handshake bytes until the box sends the longer ready message.
   for count in (12,1,1,1,1,1,1,1):
    data=s.recv(256)
    if len(data)>=24:
     # Send both press (1) and release (0), encoding the key in two nibbles.
     for p in (1,0):
      s.sendall(bytes((4,p,0,0,0,0,224+key//16,key%16)))
      time.sleep(.08)
     break
    if not data: raise RuntimeError("Remote closed")
    s.sendall(data[:count])
   else: raise RuntimeError("Handshake incomplete")
  time.sleep(.45)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.0.7")
    parser.add_argument("--list", type=Path, default=Path(__file__).with_name("sky_q_frequencies.txt"),
                        help="Read tuning settings and channel names from a text file.")
    args = parser.parse_args()
    # Validate every tuning row before sending any commands to the box.
    entries = read_entries(args.list)
    # This choice enables actual deletion through the on-screen menu.
    delete_all = input("Delete all saved manual channels before tuning? [y/N] ").strip().casefold() in {"y", "yes"}
    saved_count = 0
    if not delete_all:
        while True:
            answer = input("How many manual channels are already saved? ").strip()
            if answer.isascii() and answer.isdecimal():
                saved_count = int(answer)
                break
            print("Enter a whole number, including 0 if the list is empty.")

    print("Opening Manual Tuning from live TV.")
    send(args.host, [HOME])
    time.sleep(0.5)
    # Fixed menu offsets: Home to Settings, then Settings to Manual Tuning.
    send(args.host, [DOWN] * 12 + [SELECT])
    time.sleep(0.5)
    send(args.host, [DOWN] * 5 + [SELECT])
    # Wait for the saved-channel list to take focus before moving through it.
    time.sleep(3)

    if delete_all:
        delete_channels(args.host)
    else:
        print(f'Moving down {saved_count} rows to Add a channel.')
        send(args.host, [DOWN] * saved_count)
        time.sleep(0.5)

    # Initial dropdown defaults; subsequent scans reuse the last selected values.
    # Tuple order follows the form: polarisation, rate, FEC, standard, modulation.
    current_settings = ("V", "27.5", "2/3", "DVB-S", "QPSK")
    channels_added = saved_count
    for index, entry in enumerate(entries):
        # Pause between scans while the user saves results and returns to the list.
        if index:
            saved = input("Save the channel, then press Enter. Type 0 if you skipped it, or enter how many you saved: ").strip()
            while saved and not (saved.isascii() and saved.isdecimal()):
                saved = input("Enter the number saved, or press Enter for one: ").strip()
            # Empty input counts as one saved channel; 0 leaves the count unchanged.
            channels_added += int(saved or "1")
            send(args.host, [DOWN] * (channels_added + 1))
        current_settings = scan(args.host, entry, current_settings)


# Delete five entries at a time, or the exact remaining count supplied by the user.
def delete_channels(host):
    send(host, [RIGHT, SELECT] * 5)
    while True:
        answer = input("Continue deleting? [y/N or number of channels left] ").strip().casefold()
        if answer in {"", "n", "no", "0"}:
            return
        if answer in {"y", "yes"}:
            send(host, [RIGHT, SELECT] * 5)
        elif answer.isascii() and answer.isdecimal():
            send(host, [RIGHT, SELECT] * int(answer))
            return
        else:
            print("Enter yes, no, or the number of saved channels left.")


def scan(host, entry, current_settings):
    frequency, polarisation, standard, modulation, rate, fec, name = entry
    print(f"Scanning for {name} on {frequency} MHz")
    send(host, [SELECT])
    time.sleep(1)
    # Open frequency editing, send the five digits, then confirm the value.
    send(host, [SELECT, *map(ord, frequency), SELECT])

    targets = (polarisation, rate, fec, standard, modulation)
    # Dropdown choices in their on-screen order; offsets may move up or down.
    options_by_field = [
        ["V", "H"],
        ["22.0", "23.0", "27.5", "29.5", "29.9"],
        ["1/2", "3/5", "2/3", "3/4", "4/5", "5/6", "7/8", "8/9"],
        ["DVB-S", "DVB-S2"],
        ["QPSK", "8PSK"],
    ]
    for index, (current, target, options) in enumerate(zip(current_settings, targets, options_by_field)):
        # Move relative to the remembered selection, then confirm the target.
        offset = options.index(target) - options.index(current)
        moves = [DOWN if offset > 0 else UP] * abs(offset)
        send(host, ([LEFT] if index else []) + [DOWN, RIGHT, *moves, SELECT])

    # Return to the field list and activate Find Channels. Saving stays interactive.
    send(host, [LEFT, DOWN, SELECT])
    print(f"On the TV, select {name} and choose Save channels.")
    return targets


# Parse UTF-8 tuning rows and reject unsupported values with a line number.
def read_entries(path):
    entries = []
    allowed = [
        {"V", "H"},
        {"DVB-S", "DVB-S2"},
        {"QPSK", "8PSK"},
        {"22.0", "23.0", "27.5", "29.5", "29.9"},
        {"1/2", "3/5", "2/3", "3/4", "4/5", "5/6", "7/8", "8/9"},
    ]
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # Split once so a channel label may contain additional commas.
        settings, separator, name = line.partition(",")
        values = settings.upper().split()
        if (not separator or not name.strip() or len(values) != 6
                or len(values[0]) != 5 or not values[0].isascii() or not values[0].isdigit()
                or any(value not in options for value, options in zip(values[1:], allowed))):
            raise ValueError(f"{path}, line {number}: invalid tuning row")
        entries.append((*values, name.strip()))
    if not entries:
        raise ValueError(f"{path}: no tuning rows")
    return entries


# Report failures without continuing from an unknown on-screen position.
if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Stopped: {exc}. Check the current TV screen before retrying.")
# Sky Q Manual Tuning

This script automates the Sky Q Manual Tuning menus using remote-control commands over your local network. It reads frequencies from a text file, enters the tuning parameters and starts each scan. You select and save the channels on the TV between scans.

## Requirements

- Python 3.10 or later. No additional Python packages are required.
- A reachable Sky Q box on your local network.
- Your TV showing live television on the Sky Q box before starting.
- A frequency list beside the script named sky_q_frequencies.txt.

The default box IP is 192.168.0.7. Remote commands use TCP port 49160.

## Run the script

Open PowerShell and enter:

~~~powershell
cd C:\Users\Joey\SkyQBox
python sky_q_tuning.py
~~~

Show available options:

~~~powershell
python sky_q_tuning.py --help
~~~

## Change the IP address

For one run, supply your Sky Q box's address with --host:

~~~powershell
python sky_q_tuning.py --host 192.168.0.20
~~~

Replace the example address with the current address of your box. Check the box's Network connection and Network setup screens for its IP address.

To change the default permanently, edit this line in sky_q_tuning.py:

~~~python
parser.add_argument("--host", default="192.168.0.7")
~~~

Replace the address in default="..." and save. Supplying --host overrides the saved default.

## Frequency-file format

Each row contains six space-separated tuning values, followed by a comma and a channel label:

~~~text
FREQUENCY POLARISATION STANDARD MODULATION SYMBOL_RATE FEC, CHANNEL_LABEL
~~~

Example of the format:

~~~text
# Example tuning row
11224 H DVB-S QPSK 27.5 2/3, 7621
~~~

| Field | Accepted values |
| --- | --- |
| Frequency | Exactly five ASCII digits in MHz |
| Polarisation | V or H |
| Standard | DVB-S or DVB-S2 |
| Modulation | QPSK or 8PSK |
| Symbol rate | 22.0, 23.0, 27.5, 29.5, 29.9 |
| FEC | 1/2, 3/5, 2/3, 3/4, 4/5, 5/6, 7/8, 8/9 |
| Channel label | Nonempty text following the first comma |

Blank lines and lines beginning with # are ignored. Each row triggers a scan, including rows with repeated frequencies. The label appears in the console to help you choose channels in the results. It does not rename the broadcast channel.

The script validates all rows before sending any remote commands. Check current broadcast parameters before using a frequency list.

Use another file with --list:

~~~powershell
python sky_q_tuning.py --host 192.168.0.20 --list "C:\Users\Joey\SkyQBox\another_list.txt"
~~~

The default list is resolved beside the script. A relative path supplied through --list is resolved from the terminal's current folder.

## Follow the prompts

1. Start from live TV and launch the script.
2. Answer whether to delete existing manually tuned channels.
3. If keeping existing entries, enter the exact number already saved. Enter 0 for an empty list.
4. Watch the script navigate to Manual Tuning and enter the first frequency.
5. Select the desired channels on the TV, choose Save channels and return to the saved manual-channel list.
6. At the terminal prompt, press Enter if you saved one channel, enter 0 if you skipped it, or enter the exact number saved. This count controls navigation to the next scan.
7. Repeat for each frequency. For the final scan, save your chosen channels on the TV yourself. There is no additional save-count prompt after the final scan.

## Optional channel deletion

Choosing y or yes at the initial deletion prompt enables actual deletion. Once in Manual Tuning, the script immediately sends five Right → Select deletion sequences.

At the continuation prompt:

- Enter y or yes to send another five deletion sequences.
- Enter a number to send exactly that many deletion sequences and finish deletion.
- Press Enter, or enter n, no or 0, to stop deleting.

When using this option, complete deletion of all existing entries before proceeding. The script assumes zero existing channels after deletion. If you stop with entries remaining, interrupt the script and restart using the remaining count.

## Navigation assumptions

The script uses fixed menu positions: 12 Down presses from Home to Settings, then five Down presses to Manual Tuning. It waits for the channel list to take focus.

The first tuning form is assumed to contain V, 27.5, 2/3, DVB-S and QPSK. Later forms are assumed to retain the previous scan's settings. Dropdown movements are calculated relative to those remembered settings.

The script cannot read the TV screen or confirm that a channel was saved. Watch the TV and stop if navigation diverges from the expected menus. Firmware changes, different initial values and incorrect saved-channel counts can affect navigation.

## Stopping and troubleshooting

Press Ctrl+C in the terminal to interrupt the script. Commands already sent may have taken effect. Check the TV and return to live TV before restarting.

- Invalid tuning rows report the file and line number. Correct the input and retry.
- Connection failures can indicate a changed IP address, an unreachable box or an unavailable remote-control port.
- Remote closed and Handshake incomplete indicate that the connection did not complete.
- If the wrong menu is selected, stop and check the starting screen, menu positions and saved-channel count.
- If a scan fails to find the desired channel, verify its current broadcast parameters.

## Licence and attribution

Copyright (c) 2026 Joey Tatú.

This project uses the MIT License in LICENCE. You may use, copy, modify and distribute the code, including commercially. Retain the copyright notice and licence text in copies or substantial portions, including modified copies.

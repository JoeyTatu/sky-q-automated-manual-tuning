# Sky Q Manual Tuning

This script automates the Sky Q Manual Tuning menus using remote-control commands over your local network. It reads frequencies from a text file, enters the tuning parameters and starts each scan. You select and save the channels on the TV between scans.

## Requirements

- Python 3.10 or later. No additional Python packages are required.
- A reachable Sky Q box on your local network.
- Your TV showing live television on the Sky Q box before starting.
- A frequency list beside the script named sky_q_frequencies.txt.

The default box IP is 192.168.0.7. Remote commands use TCP port 49160.

## Download the project

1. Open [sky-q-automated-manual-tuning on GitHub](https://github.com/JoeyTatu/sky-q-automated-manual-tuning).
2. Select **Code → Download ZIP**.
3. Extract the ZIP using your operating system's archive tool.
4. Locate the project folder containing sky_q_tuning.py, sky_q_frequencies.txt, README.md and LICENCE. You can name the folder sky-q-automated-manual-tuning. ZIP downloads may include a branch suffix such as -main.

Alternatively, with Git installed, run:

~~~sh
git clone https://github.com/JoeyTatu/sky-q-automated-manual-tuning.git
~~~

This creates a folder named sky-q-automated-manual-tuning inside the terminal's current folder. Keep the script and default frequency list together.

## Run the script

Open a terminal on Windows, macOS or Linux and navigate to the folder where you extracted or cloned the project. You can use cd followed by the folder's path in quotes. Use the actual location you chose when downloading.

Once the terminal is in the folder containing sky_q_tuning.py, run:

~~~sh
python sky_q_tuning.py
~~~

On systems where Python 3 is available as python3, use:

~~~sh
python3 sky_q_tuning.py
~~~

Check that your chosen command reports Python 3.10 or later with python --version or python3 --version. Use that same command for all examples below.

Show available options:

~~~sh
python sky_q_tuning.py --help
~~~

## Change the IP address

For one run, supply your Sky Q box's address with --host:

~~~sh
python sky_q_tuning.py --host 192.168.0.20
~~~

Replace the example address with the current address of your box. Check the box's Network connection and Network setup screens for its IP address.

To change the default IP address inside the code:

1. Open sky_q_tuning.py in a plain-text editor.
2. Find line 51 in the current version, or search for parser.add_argument("--host". Line numbers may change in later versions.
3. Locate this line:

~~~python
parser.add_argument("--host", default="192.168.0.7")
~~~

4. Replace only the address between the quotes after default=. For example, if your Sky Q box has the address 192.168.0.20, use:

~~~python
parser.add_argument("--host", default="192.168.0.20")
~~~

5. Save the file, then run the script again. It will use the new default address.

Enter the current local IP address assigned to your Sky Q box. Both the box's address and your router's address depend on your network. Check the Sky Q box's network information and use the address shown for the box.

The addresses in the header comments are examples. The --host argument on line 51 controls the default connection address. Supplying --host on the command line overrides that default for the current run.

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

~~~sh
python sky_q_tuning.py --host 192.168.0.20 --list "another_list.txt"
~~~

The default list is resolved beside the script. A relative path supplied through --list is resolved from the terminal's current folder.

## Edit or create a frequency list

1. Close any running tuning script before editing its list.
2. Open sky_q_frequencies.txt in a plain-text editor, such as Notepad on Windows, TextEdit in plain-text mode on macOS, or a text editor on Linux.
3. Add, change, remove or reorder rows using the format described above. Use current tuning parameters for the channels you want.
4. Save the file as UTF-8 plain text, then run the script again. Use Ctrl+S on Windows/Linux or Command+S on macOS.

For example, changing a frequency means replacing the first five digits on its row. If the broadcaster also changed polarisation, symbol rate, FEC, standard or modulation, update those fields too. Keep the comma before the channel label. The example rows demonstrate file format and are not checked live against satellite listings.

The script scans rows from top to bottom. To select several channels from one frequency, you can use one row with a descriptive label:

~~~text
11224 H DVB-S QPSK 27.5 2/3, Select the channels you want from these results
~~~

Choose and save the channels on the TV, then tell the script exactly how many you saved. Entering several rows with identical tuning parameters causes repeated scans of that frequency.

To preserve the supplied list, save a copy named another_list.txt in the project folder. Keep UTF-8 encoding and plain-text format. Check that the editor has not added an extra extension, such as another_list.txt.txt, or saved the file as a rich-text document.

Run your custom list with:

~~~sh
python sky_q_tuning.py --list "another_list.txt"
~~~

You can also supply --host when the box uses a different IP address. The script loads the list once at startup, so restart it to use subsequent edits.

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

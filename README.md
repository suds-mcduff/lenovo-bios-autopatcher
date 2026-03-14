# lenovo-bios-autopatcher
Since Badcaps forum now requires a paid account to access download links, the lenovo bios auto-patcher from Knucklegrumble cannot be accessed. I paid the £6 and have re-uploaded the source code here. As per Knucklegrumble's forum post: "You CAN download it, modify it, redistribute it".

[Original Badcaps forum post](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-laptops-tablets-and-mobile-devices/bios-requests-only/78215-lenovo-bios-auto-patcher-for-supervisor-password-removal)

This is the forum post, pasted here:

Hello everyone!

In the past several weeks I've learned a lot from this forum and its community especially from all the folks who contributed to THIS thread

With some trial and error I was able to reliably patch BIOS dumps for SVP-locked Lenovo machines up to the 8th generation using the info, tools, and files provided on this forum. After some practice and positive feedback from users I helped I've noticed that, once learned, the process is fairly straightforward, so I've developed a small python script to automate it and allow everyone to patch their own binaries without having to ask for help and wait.

This is my way to give back to the community. Also I am lazy... lol.

**DISCLAIMER**

THIS SCRIPT IS FREE AND IS INTENDED FOR EDUCATIONAL PURPOSES ONLY.
You CAN download it, modify it, redistribute it, etc. I only ask that you DON'T sell it or try to make a profit from it, and that you please credit the authors for the time and work they put into it.
I TAKE NO CREDIT FOR CREATING THE DXE DRIVERS OR ANY OF THE FILES THAT MAKE UP THE PATCH ITSELF.
I've only developed the python script that automates the process and puts it all together.
I TAKE NO RESPONSIBILITY FOR ANY DAMAGE YOU DO TO YOUR MACHINE, YOUR PETS, YOUR HOUSE, YOUR LIFE, AND THE SPACE-TIME CONTINUUM
Making this kind of modifications is risky and might leave you with an unusable/broken machine.
The script is not perfect by any means, and while I haven't bricked any hardware (yet) I can't promise that won't happen to you.
USE IT AT YOUR OWN RISK.

With that out of the way, using it is pretty simple and it should work on both Windows and Linux as long as you have Python installed https://www.python.org/downloads/.
Just download the zip file and extract it. You'll get a folder named "lenovo_autopatcher" with the following content:

IMPORTANT: Before applying the patch make sure you verify that your original image is not corrupted by dumping 1 or 2 additional images from your bios chip and comparing them. The original dump is THE ONLY WAY to recover your machine if something goes wrong!

From command line use either autopatch.cmd (Windows) or autopatch.sh (Linux) as follows:

autopatch <your_bios_image.ext>

**THAT'S IT!**

The command will generate either your_bios_image_PATCHED.ext or your_bios_image_PATCHED_CLEAN.ext depending on the type of BIOS you are patching. The original dump will be left unchanged.

`autopatch -h` will output the help info for the command
`autopatch --howto` will output the following instructions on how to use the patched image:

**[ HOW TO USE THE PATCH ]**

STEP 1: Flash and replace current BIOS with the generated patch file

STEP 2: Boot the machine

STEP 3: Press ENTER/F1/etc. to enter BIOS settings

STEP 4: Enter any character when asked for Supervisor Password

STEP 5: Press enter when it shows Hardware ID

STEP 6: Press space bar 2x when asked

STEP 7: Turn off machine

STEP 8: Restore original BIOS

STEP 9: Reset BIOS settings to factory default


**[ NOTES ]**

When booting the patched BIOS you might have to:
- Hold the anti-tamper switch down the whole time (use tape)
- Remove the hard disk or replace it with a locked one

Finally, I would be grateful if you could report any bugs, errors, problems, or general feedback in this thread so that I can make improvements to the script.

Thank you, and enjoy!

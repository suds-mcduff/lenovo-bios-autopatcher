#! /usr/bin/python
from argparse import RawTextHelpFormatter
import argparse
import binascii
import uuid
import os
import subprocess
import shutil
import glob
import platform


VERSION = '0.2'

parser = argparse.ArgumentParser(prog="autopatch",
                                 description="Automatically Patch Lenovo BIOS dump to generate a Supervisor Password "
                                             "Unlock flashable file.\n"
                                             "Works on all Lenovo laptops up to the 8th generation.")
parser.formatter_class = RawTextHelpFormatter

parser.add_argument('--howto', action='store_true', help='show HOW TO instructions')
parser.add_argument('--version', action='store_true', help='output script version')
parser.add_argument('source', metavar='BIN', nargs='?', help='original bios dump file')

args = parser.parse_args()


def show_how_to(clean_file=None):
    if not clean_file:
        clean_file = 'the generated patch file'
        print('')
        print('-= INSTRUCTIONS =-')
        print('')
        print('First use command "autopatch <original_bios_binaries>" to generate the patch image to flash.')

    print('')
    print('[ HOW TO USE THE PATCH ]')
    print('STEP 1: Flash and replace current BIOS with ' + clean_file)
    print('STEP 2: Boot the machine')
    print('STEP 3: Press ENTER/F1/etc. to enter BIOS settings')
    print('STEP 4: Enter any character when asked for Supervisor Password')
    print('STEP 5: Press enter when it shows Hardware ID')
    print('STEP 6: Press space bar 2x when asked')
    print('STEP 7: Turn off machine')
    print('STEP 8: Restore original BIOS')
    print('STEP 9: Reset BIOS settings to factory default')
    print('')
    print('[ NOTES ]')
    print('When booting the patched BIOS you might have to:')
    print(' - Hold the anti-tamper switch down the whole time (use tape)')
    print(' - Remove the hard disk or replace it with a locked one')
    print('')
    print('For questions and feedback visit')
    print('https://www.badcaps.net/forum/showthread.php?p=981152')
    print('')
    print('Good luck.')


def hex_to_guid(hex):
    h = binascii.unhexlify(hex)

    data1 = h[0:4][::-1]
    data2 = h[4:6][::-1]
    data3 = h[6:8][::-1]
    data4a = h[8:10]
    data4b = h[10:16]

    components = [data1, data2, data3, data4a, data4b]

    hex_bytes = [binascii.hexlify(d) for d in components]
    decoded = [bytes.decode(b) for b in hex_bytes]

    return '-'.join(decoded)


def guid_to_hex(guid):
    guid = uuid.UUID(guid).hex
    g = binascii.unhexlify(guid)

    data1 = g[0:4][::-1]
    data2 = g[4:6][::-1]
    data3 = g[6:8][::-1]
    data4 = g[8:]

    components = [data1, data2, data3, data4]

    hex_bytes = [binascii.hexlify(d) for d in components]
    decoded = [bytes.decode(b) for b in hex_bytes]

    return ''.join(decoded)


def path_to(filepath):
    exec_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
    return os.path.join(exec_path, filepath)


def load_binary(source_file):
    with open(source_file, 'rb') as f:
        content = f.read()
    return content


def file_guid(filepath):
    with open(filepath, 'rb') as f:
        data = f.read(16)
    hex_byets = binascii.hexlify(data)
    return hex_to_guid(hex_byets)


def replace(body, content, guid):
    hex_guid = guid_to_hex(guid)
    offset = body.find(hex_guid)
    length = len(content) + offset
    if offset < 0:
        print('... Not found. Skipping.')
        return body
    else:
        print('... Cleaned.')
        return body[:offset] + content + body[length:]


def write_binary(content, destination_path):
    with open(destination_path, 'wb') as fb:
        fb.write(content)


def patch(source_file):
    executable = None
    if platform.system() == 'Windows':
        executable = 'UEFIReplace.exe'
    elif platform.system() == 'Linux':
        executable = 'UEFIReplace'
    else:
        print('OS not supported')
        exit()

    if not os.path.exists(source_file):
        print('File "' + source_file + '" not found.')
        exit()

    file = os.path.splitext(source_file)
    patched_filename = file[0] + '_PATCHED' + file[1]
    shutil.copyfile(source_file, patched_filename)

    path = path_to('patch/DXE/*')
    drivers = glob.glob(path)
    total = str(len(drivers))

    print('\nUsing UEFIReplace to inject ' + total + ' DXE drivers...')

    current = 1
    for driver in drivers:
        name = os.path.splitext(os.path.basename(driver))[0]
        guid = file_guid(driver)
        print('[' + str(current) + '/' + total + '] ' + name + ' (GUID ' + guid + ')')
        code = subprocess \
            .call([path_to('tools/'+executable), patched_filename, guid, '07', driver, '-asis', '-all', '-o', 'temp.bin'],
                  stdout=subprocess.PIPE)

        os.remove(patched_filename)

        if code > 0:
            print(source_file + ' is corrupted or does not contain a valid dump.')
            print('There was an error... Aborting.')
            exit()

        os.rename('temp.bin', patched_filename)
        current += 1

    clean(patched_filename)


def clean(source_file):
    source = load_binary(source_file)

    print('\nLooking for volumes to patch...')

    # patched = os.path.splitext(source_file)
    # clean_filename = patched[0]+'_CLEAN'+patched[1]

    patches = glob.glob(path_to('patch/VOLUMES/*'))
    total = str(len(patches))

    current = 1
    for p in patches:
        name = os.path.splitext(os.path.basename(p))[0]
        volume = load_patched_volume(p)
        print('[' + str(current) + '/' + total + '] ' + name + ' (checksum ' + volume['checksum'] + 'h):')
        source = replace_volume(source, volume)

        current += 1

    write_binary(source, source_file)

    # os.remove(source_file)

    print('\nDone.')

    patched_basename = os.path.basename(source_file)

    if args.howto:
        show_how_to(patched_basename)
    else:
        print('\nPATCH FILE: ' + patched_basename)
        print('\nGood luck.')


def replace_volume(source, volume):
    target_volume = find_volume_to_patch(source, volume['pattern'])

    if target_volume:
        print('      Found volume at offset ' + target_volume['offset'] + 'h (checksum ' + target_volume['checksum'] + 'h)')
        if volume['size'] != target_volume['size']:
            print('      Volume size does not match... Skipping.')
        elif volume['checksum'] != target_volume['checksum']:
            print('      Volume checksum does not match... Skipping.')
        else:
            position = target_volume['position']
            length = position+target_volume['size']
            print('      Replacing volume.')
            return source[:position] + volume['content'] + source[length:]

    else:
        print('      Not found... Skipping.')

    return source


def load_patched_volume(file):
    content = load_binary(file)
    pattern = content[:48]
    header = content[16:72]
    size = int.from_bytes(header[16:19], 'little')
    body = content[72:]
    signature = header[24:28].decode()
    checksum = binascii.hexlify(header[34:36]).decode()
    return {
        'content': content,
        'pattern': pattern,
        'header': header,
        'body': body,
        'signature': signature,
        'size': size,
        'checksum': checksum
    }


def find_volume_to_patch(file, pattern):
    content = file
    position = content.find(pattern)
    if not position < 0:
        header_offset = position+16
        body_offset = position+72
        header = content[header_offset:body_offset]
        size = int.from_bytes(header[16:19], 'little')
        body = content[body_offset:position+size]
        signature = header[24:28].decode()
        offset = position.to_bytes(3, 'big').hex()
        checksum = binascii.hexlify(header[34:36]).decode()
        return {
            'position': position,
            'offset': offset,
            'header': header,
            'body': body,
            'signature': signature,
            'size': size,
            'checksum': checksum
        }
    else:
        return False


def needs_cleaning(body):
    for v in glob.glob(path_to('patch/NVRAM/*')):
        guid = os.path.splitext(os.path.basename(v))[0]
        hex_guid = guid_to_hex(guid)
        offset = body.find(hex_guid)
        if offset < 0:
            return False

    return True



filename = args.source

if args.version:
    print('\nLenovo Auto-Patcher v'+VERSION)
    print("\nCredits for the patch go to all the folks who contributed on")
    print("https://www.badcaps.net/forum/showthread.php?t=65996")
    print("\nAuto-Patcher developed by Knucklegrumble.")
    exit()

if not filename:
    if args.howto:
        show_how_to()
    else:
        print('usage: autopatch [-h] [--howto] [BIN]')
else:
    patch(filename)
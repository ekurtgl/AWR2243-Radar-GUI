import os
import subprocess


sudo_password = '190396'
cwd = '/home/emre/Desktop/77ghz/CLI/Release'
radar_path = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/' \
             'open_radar_initiative-new_receive_test/setup_radar/build'
radar_cmd = './setup_radar'
export_cmd = 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd'
os.environ["LD_LIBRARY_PATH"] = cwd  # + ':' + os.getcwd() # error code 127 when not executed

fpga_cmd = './DCA1000EVM_CLI_Control fpga cf.json'.split()
record_cmd = './DCA1000EVM_CLI_Control record cf.json'.split()

pwd = subprocess.Popen(['echo', sudo_password], cwd=radar_path, stdout=subprocess.PIPE)
pwd.wait()
print('sudopass: ', pwd.stdout.read())

cmd = subprocess.Popen(['sudo', '-S'] + [radar_cmd], cwd=radar_path, stdin=pwd.stdout,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
cmd.wait()
print('setup_radar error return code: ', cmd.stderr.read())

cmd = subprocess.Popen(fpga_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
cmd.wait()
print('fpga error return code: ', cmd.returncode)
# print('fpga error2: ', cmd.stderr.read())
# print('fpga stdout: ', cmd.stdout.read())

cmd = subprocess.Popen(record_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
cmd.wait()
# cmd.stdin.write("record cf.json")
# cmd.wait()

print('record error return code: ', cmd.returncode)
# print('record error2: ', cmd.stderr.read())
# print('record stdout: ', cmd.stdout.read())

if cmd.returncode == 0:
    print('Radar is ready to go!')
else:
    print('Radar setup error!')








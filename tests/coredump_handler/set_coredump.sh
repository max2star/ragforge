ulimit -c
cat /proc/sys/kernel/core_pattern
#ulimit -c unlimited
##/etc/security/limits.conf
##*               soft    core            unlimited
##*               hard    core            unlimited
#mkdir -p  /opt/coredumps
#echo "kernel.core_pattern = /opt/coredumps/core-%e-%s-%u-%g-%p-%t" >> /etc/sysctl.conf
#echo "kernel.core_uses_pid = 0" >> /etc/sysctl.conf
#sysctl -p
#
# 创建一个会崩溃的测试程序
# 运行测试程序
echo 'int main(){int *p=0;*p=1;}' > test.c
gcc test.c -o test
./test
gdb /path/to/executable /path/to/corefile

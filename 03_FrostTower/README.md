# Challenge 3: That Frost Tower's Entrance 

> Turn up the heat to defrost the entrance to Frost Tower. Click on the Items tab in your badge to find a link to the Wifi Dongle's CLI interface. Talk to Greasy Gopherguts outside the tower for tips.

## The Hint

We can meet up with Greasy in the main North Pole area.  Here's what he has to say:

> Grnph. Blach! Phlegm.
> 
> I'm Greasy Gopherguts. I need help with parsing some Nmap output.
> 
> If you help me find some results, I'll give you some hints about Wi-Fi.
> 
> Click on the terminal next to me and read the instructions.
> 
> Maybe search for a cheat sheet if the hints in the terminal don't do it for ya'.
> 
> You’ll type quizme in the terminal and grep through the Nmap bigscan.gnmap file to find answers.

The terminal prompts us with the following challenge:

> Howdy howdy!  Mind helping me with this homew- er, challenge?
> Someone ran nmap -oG on a big network and produced this bigscan.gnmap file.
> The quizme program has the questions and hints and, incidentally,
> has NOTHING to do with an Elf University assignment. Thanks!
> 
> Answer all the questions in the quizme executable:
> - What port does 34.76.1.22 have open?
> - What port does 34.77.207.226 have open?
> - How many hosts appear "Up" in the scan?
> - How many hosts have a web port open?  (Let's just use TCP ports 80, 443, and 8080)
> - How many hosts with status Up have no (detected) open TCP ports?
> - What's the greatest number of TCP ports any one host has open?
> 
> Check out bigscan.gnmap and type quizme to answer each question.

We can see we are dealing with a fairly large file, so as Greasy had indicated, we will need to use grep to find the answers to the questions:

```bash
elf@397cb6df9b81:~$ ls -lh
total 5.5M
-rw-r--r-- 1 root root 5.5M Nov 23 15:48 bigscan.gnmap
```

Using grep we can get answers:

```bash
elf@397cb6df9b81:~$ grep 34.76.1.22 bigscan.gnmap 
Host: 34.76.1.22 ()     Status: Up
Host: 34.76.1.22 ()     Ports: 62078/open/tcp//iphone-sync///      Ignored State: closed (999)
elf@397cb6df9b81:~$ grep 34.77.207.226 bigscan.gnmap 
Host: 34.77.207.226 ()     Status: Up
Host: 34.77.207.226 ()     Ports: 8080/open/tcp//http-proxy///      Ignored State: filtered (999)
elf@397cb6df9b81:~$ grep "Status: Up" bigscan.gnmap | wc -l
26054
elf@397cb6df9b81:~$ egrep '(80|443|8080)/open'  bigscan.gnmap | wc -l
14372
elf@397cb6df9b81:~$ expr `grep "Status: Up" bigscan.gnmap | wc -l` - `grep "Status: Up" bigscan.gnmap -a1 | grep -v "Status: Up" | wc -l` + 1
402
elf@397cb6df9b81:~$ expr `cat bigscan.gnmap | awk ' { if ( length > x ) { x = length; y = $0 } }END{ print y }' | tr -cd , | wc -c` + 1
12
```

Here's what Greasy has to pass on after we complete his challenge:

> Grack. Ungh. ... Oh!
> 
> You really did it?
> 
> Well, OK then. Here's what I know about the wifi here.
> 
> Scanning for Wi-Fi networks with iwlist will be location-dependent. You may need to move around the North Pole and keep scanning to identify a Wi-Fi network.
> 
> Wireless in Linux is supported by many tools, but iwlist and iwconfig are commonly used at the command line.
> 
> The curl utility can make HTTP requests at the command line!
> 
> By default, curl makes an HTTP GET request. You can add --request POST as a command line argument to make an HTTP POST request.
> 
> When sending HTTP POST, add --data-binary followed by the data you want to send as the POST body.

## The Main Challenge

Firing up the WiFi dongle, we get the following prompt:

```bash
                         ATTENTION ALL ELVES

In Santa's workshop (wireless division), we've been busy adding new Cranberry
Pi features. We're proud to present an experimental version of the Cranberry
Pi, now with Wi-Fi support!

This beta version of the Cranberry Pi has Wi-Fi hardware and software
support using the Linux wireless-tools package. This means you can use iwlist
to search for Wi-Fi networks, and connect with iwconfig! Read the manual
pages to learn more about these commands:

man iwlist

man iwconfig

I'm afraid there aren't a lot of Wi-Fi networks in the North Pole yet, but if
you keep scanning maybe you'll find something interesting.

                                                 - Sparkle Redberry



elf@c4cc97284d87:~$
```

If we walk over to Frost Tower and open up the dongle again, we can see a new SSID reporting:

```bash
elf@f95643a01f38:~$ iwlist scan
wlan0     Scan completed :
          Cell 01 - Address: 02:4A:46:68:69:21
                    Frequency:5.2 GHz (Channel 40)
                    Quality=48/70  Signal level=-62 dBm  
                    Encryption key:off
                    Bit Rates:400 Mb/s
                    ESSID:"FROST-Nidus-Setup"
          
elf@f95643a01f38:~$ iwconfig wlan0 essid "FROST-Nidus-Setup"
** New network connection to Nidus Thermostat detected! Visit http://nidus-setup:8080/ to complete setup
(The setup is compatible with the 'curl' utility)
```

Let's try curling the setup URL:

```bash
elf@f95643a01f38:~$ curl http://nidus-setup:8080
◈──────────────────────────────────────────────────────────────────────────────◈

Nidus Thermostat Setup

◈──────────────────────────────────────────────────────────────────────────────◈

WARNING Your Nidus Thermostat is not currently configured! Access to this
device is restricted until you register your thermostat » /register. Once you
have completed registration, the device will be fully activated.

In the meantime, Due to North Pole Health and Safety regulations
42 N.P.H.S 2600(h)(0) - frostbite protection, you may adjust the temperature.

API

The API for your Nidus Thermostat is located at http://nidus-setup:8080/apidoc
```

Let's check out the api documentation:

```bash
elf@f95643a01f38:~$ curl http://nidus-setup:8080/apidoc
◈──────────────────────────────────────────────────────────────────────────────◈

Nidus Thermostat API

◈──────────────────────────────────────────────────────────────────────────────◈

The API endpoints are accessed via:

http://nidus-setup:8080/api/<endpoint>

Utilize a GET request to query information; for example, you can check the
temperatures set on your cooler with:

curl -XGET http://nidus-setup:8080/api/cooler

Utilize a POST request with a JSON payload to configuration information; for
example, you can change the temperature on your cooler using:

curl -XPOST -H 'Content-Type: application/json' \
  --data-binary '{"temperature": -40}' \
  http://nidus-setup:8080/api/cooler


● WARNING: DO NOT SET THE TEMPERATURE ABOVE 0! That might melt important furniture

Available endpoints

┌─────────────────────────────┬────────────────────────────────┐
│ Path                        │ Available without registering? │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/cooler                 │ Yes                            │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/hot-ice-tank           │ No                             │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/snow-shower            │ No                             │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/melted-ice-maker       │ No                             │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/frozen-cocoa-dispenser │ No                             │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/toilet-seat-cooler     │ No                             │ 
├─────────────────────────────┼────────────────────────────────┤
│ /api/server-room-warmer     │ No                             │ 
└─────────────────────────────┴────────────────────────────────┘
```

Sending a `GET` request to the cooler api endpoint gives us its current configuration:

```bash
elf@f95643a01f38:~$ curl http://nidus-setup:8080/api/cooler
{
  "temperature": -39.46,
  "humidity": 58.01,
  "wind": 10.69,
  "windchill": -50.87
}
```

Let's try adjusting the temperature to something a bit warmer with a `POST` request:

```bash
elf@f95643a01f38:~$ curl -XPOST -H 'Content-Type: application/json' --data-binary '{"temperature": 70}' http://nidus-setup:8080/api/cooler
{
  "temperature": 69.07,
  "humidity": 60.89,
  "wind": 10.9,
  "windchill": 79.52,
  "WARNING": "ICE MELT DETECTED!"
}
```

Success!
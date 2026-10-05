<!-- 📌 Japleen K.: edit ONLY inside this folder (/japleen-k). Fill in every section below, replacing [placeholders] with your own words. Delete this comment when you start. -->

# Project Title


**Track:**   Hardware and Software Orchestration
**Candidate:** Japleen K.  
**Github Username**: japleenkCODES  
**Phone Number**: 7428927898
**Email ID**: japleenk21380@gmail.com

---

## 1. Overview

### What & Why
What did you build, what does it do, and why did you choose it?
I built a Panic/Emergency and Check In Button for the elderly, which can be very helpful in determining and taking care of your loved ones.
In case of an emergency it can be used as a quick alarm that sends notifications to the contacts to help them. It also helps to keep check time to time check on them.

I chose this project as it would be helpful for many families in the Indian modern household where parents are generally not living with their children in the cities, and it could be quickly used to get alerted on their health. 

### Expected Outcome
This can achieve fast emergency response by alerting the contacts registered in the application, saving lives.

---

## 2. Requirements

### Hardware
| Component | Qty | Purpose |
|---|---:|---|
| ESP8266 | 1 | Used As the remote |
| Push Buttons | 2 | Used in the remote |
| Server | 1 | Used as a server for the backend and sending notifications |

### Software
| Tool / Library | Version | Purpose |
|---|---|---|
| Python/Flask Server | 3.11 | Web-Server |
| pycloudflared | 0.2.0 | Cloudflare Tunnel |
| Unity | 6.3 | Android App |


**Constraints:** 

1. Currently the server does not account for different time zones
2. Check-in Alarms don't turn off while sleeping.

These problems can be solved easily by converting times to standard IST or UTC 00:00.
Check-in problem can be solved by adding sleep switch that adds a 8-10 hour to the check-in time.

---

## 3. Design

### System Overview
A Flask Server runs continuously picking up requests made to it and classifying them into two types,
    1. Check In
    2. Emergency

A clock on the server keeps running that checks if the checkin time is greater than a predefined check-in time threshold and if it exceeds it, it sends a notification to the family.

The Emergency button immediately sends a notification to the family and neighbors, that can be helpful to alert the emergency services.  


![System Diagram](./docs/images/system-overview.png)

### Key Decisions
What did you choose, why, and what did you reject?

1. Choosing ESP ``` I chose esp8266 over arduino for wifi support and cost efficiency ```
2. Choosing Flask over other servers like Django ``` Flask is lighter for the server than Django and allows over modularibility ```
3. Unity App ``` The Remote can be replaced by a simple app for ease of use  ```

---

## 4. Implementation

![Server](./src/app.py)
The Server uses threading to run two threads, One for the continuous clock and other for sending notifications.

![Unity App Source](./src/UnityProject)
Unity Project for the android app.

![APK](./src/UnityProject/panic_button.apk)
Installable apk, with qr scanning, server connection and panic and emergency buttons.

---

## 5. Demonstration

Cover **every assigned demonstration requirement**.

I need your requirement + need elegantly here, you could simply insert a youtube link for the recordings, No issues!

---

## 6. Final Result

### Working
- Emergency Button
- Check-in Button
- Configurable Server and Server URL
- QR Scanning

### Known Issues
- Different Timezones cause problems
- No Sleep timer included

**Demo:** [Video Link]


---

## 7. Limitations & Improvements

**Limitations:** 
- Different Timezones cause problems
- No Sleep timer included

**Next Steps:** 
- Adding a sleep switch
- Adding timezones

---

## 8. Key Learnings

Hardware implementation, Learning about web servers, python. This can be a very helpful project to many indian families

---

<!-- Update
## 9. Repository Structure

```text
project-name/
├── README.md
├── src/
├── hardware/
├── docs/
├── tests/
└── media/
```
>

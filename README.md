

\## Setup



\### 1. Clone \& Enter

```bash

git clone https://github.com/mugunthragav/mail_responding_agent.git

cd mail_responding_agent

```



\### 2. Create `.env`


Edit `.env`:

```env

OPENAI_API_KEY=sk-...

GMAIL_EMAIL=you@gmail.com

GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx   # with spaces

DASH_DEBUG=False

```



---



\### 3. Generate Gmail App Password (Required)



> \*\*You must use a Gmail App Password — not your regular password.\*\*



\#### Step-by-Step:



1\. Go to: \[https://myaccount.google.com/apppasswords]  

&nbsp;  \*(You may need to enable 2-Factor Authentication first)\*



2\. \*\*Enable 2-Factor Authentication (if not already)\*\*  

&nbsp;  → Google Account → Security → 2-Step Verification → Turn On



3\. Go back to \*\*App passwords\*\*  

&nbsp;  → Give a name for your app and click Create 



4\. \*\*Copy the 16-character password\*\* (e.g., `crzg kbtr ftgg yadw`)  

&nbsp;  → \*\*Paste exactly into `.env`\*\* (with spaces, no quotes)



&nbsp;  ```env

&nbsp;  GMAIL\_APP\_PASSWORD=caed ktyt ferg yera

&nbsp;  ```



> \*\*Do NOT use your main Gmail password\*\*  

> \*\*Do NOT remove spaces\*\*



---



\### 4. Run

```bash

docker-compose up --build

```



Open: \[http://localhost:8050]



---



\## UI Usage



1\. \*\*Click "Refresh Live Emails"\*\*  

&nbsp;  → Fetches 10 \*\*unread\*\* emails  

&nbsp;  → \*\*All fields reset\*\*



2\. \*\*Select an email\*\*  

&nbsp;  → Shows: Subject, From, Body  

&nbsp;  → \*\*Category badge\*\* (URGENT / WORK / PERSONAL / SPAM)  

&nbsp;  → \*\*AI Draft\*\* appears instantly



3\. \*\*Enter feedback\*\* → Click \*\*Refine Draft\*\*  

&nbsp;  → Improved reply  

&nbsp;  → Feedback \*\*saved \& reused\*\* later  

&nbsp;  → Input auto-clears



4\. \*\*Memory in Action\*\*  

&nbsp;  → Type: `"Use the same tone as last time"`  

&nbsp;  → AI recalls your style



---
5\. \*\*YouTube Unlisted Video Link\*\*
https://youtu.be/zae4NFZB6Lo



\## Troubleshooting



| Issue | Solution |

|------|----------|

| `python-dotenv could not parse` | No comments, no quotes in `.env`. Use exact format |

| No emails loaded | Enable \*\*IMAP\*\* in Gmail → Settings → Forwarding and POP/IMAP |

| App password invalid | Regenerate at \[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) → \*\*include spaces\*\* |

| Port 8050 in use | Run `docker-compose down` first |

| Memory not saving | `./data` is mounted → check folder exists |

| Long emails crash UI | Body truncated in UI (full used in LLM) |






# MBOA FINANCE AI — 3-MINUTE DEMONSTRATION & VIDEO RECORDING SCRIPT

**Competition:** SAFINUM Innovate Challenge — Cameroon  
**Time Limit:** 3 Minutes  
**Demonstrator:** Emmanuel Rostand / Team Lead  

---

## 1. Preparation Checklist
1. Open terminal and run:
   ```powershell
   .\.venv\Scripts\python.exe run_backend.py
   ```
2. Open your web browser to: [`http://127.0.0.1:8000/bank`](http://127.0.0.1:8000/bank)
3. Ensure microphone and audio speakers are unmuted.

---

## 2. Minute-by-Minute Script

### [00:00 - 00:35] The Hook & Problem Statement
- **Speaker:**  
  *"Hello judges and members of the SAFINUM Innovate Challenge jury. Digital finance in Cameroon is booming with over 15 million Mobile Money and microfinance users. Yet, millions of rural citizens, market traders, and elderly people cannot use these services because they are in administrative French or English, and require reading smartphone screens.*  
  *Today, we present **Mboa Finance AI**: the first autonomous, voice-first, multilingual accessibility agent that enables anyone to use existing financial websites using their spoken mother tongue."*

---

### [00:35 - 01:20] Live Demonstration 1: Fulfulde Voice Interaction & DOM Inspection
- **Action:**  
  Click the floating green **Mboa AI** microphone bubble in the bottom right corner of [`http://127.0.0.1:8000/bank`](http://127.0.0.1:8000/bank).
- **Speaker:**  
  *"Let's observe our agent in action. A Fulani merchant from Maroua or Garoua opens this portal and speaks in Fulfulde:"*
- **Action:**  
  Select **Fulfulde** in the dropdown and click the quick chip: **"Holle yam ceede am keddiiɗe"** (or speak into the microphone).
- **What happens on screen:**  
  1. The agent analyzes the live DOM.
  2. Extracts the balance: `150 000 FCFA`.
  3. Synthesizes a natural spoken response in Fulfulde: *"Ceede maada keddiiɗe ɗon: 150 000 FCFA."*
  4. Plays back the audio automatically.

---

### [01:20 - 01:55] Live Demonstration 2: In-Place Translation & Dynamic Alert Ingestion
- **Speaker:**  
  *"Next, what happens if an Ewondo speaker from Yaoundé wants the entire webpage localized into their language?"*
- **Action:**  
  Click the quick chip: **"Fiti foé nyi e Ewondo"** (or type *"Traduire la page en Ewondo"*).
- **What happens on screen:**  
  1. The agent uses Microsoft Playwright to traverse DOM text nodes without breaking styles.
  2. The page text live translates in place, preserving amounts, phone numbers, and buttons.
- **Action:**  
  Click the **"🔔 Déclencher alerte dynamique"** button on the portal.
- **Speaker:**  
  *"Our MutationObserver immediately detects the newly introduced maintenance alert in real-time, extracts it, and translates it without rebuilding or refreshing the application."*

---

### [01:55 - 02:40] Live Demonstration 3: Deterministic Financial Safety & Two-Phase Transfer
- **Speaker:**  
  *"Now comes our most critical innovation: **Deterministic Financial Integrity**."*
- **Action:**  
  Click the chip: **"💸 Envoyer 25 000 FCFA au 699001122"**.
- **What happens on screen:**  
  1. The agent pre-fills the transfer form on the bank interface.
  2. The Financial Integrity Engine deterministically computes:
     $\text{Amount: } 25,000 \text{ FCFA} + \text{Fee: } 250 \text{ FCFA} = \text{Total: } 25,250 \text{ FCFA}$.
  3. The agent pops up a **Yellow Confirmation Card** inside the assistant window.
- **Speaker:**  
  *"Notice that the agent HAS NOT submitted the transaction. An LLM is never allowed to hallucinate or finalize money movement autonomously. The user is presented with the exact figures and must explicitly confirm."*
- **Action:**  
  Click **"✓ Confirmer"** in the assistant panel.
- **What happens on screen:**  
  The agent marks the transaction `CONFIRMED`, triggers the simulated banking submission, and displays the success banner.

---

### [02:40 - 03:00] Closing & Scalability
- **Speaker:**  
  *"Mboa Finance AI is 100% functional today. It is containerized in Docker, backed by 14 automated tests, and designed as a drop-in SDK for Cameroonian banks and microfinances. With Mboa Finance AI, we turn digital financial inclusion into a tangible reality for every Cameroonian citizen. Thank you."*


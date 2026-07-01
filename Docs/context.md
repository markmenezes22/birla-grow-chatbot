# Project Context: Mutual Fund FAQ Assistant

## Overview
A Retrieval-Augmented Generation (RAG)-based facts-only FAQ assistant for mutual fund schemes. The assistant answers objective, verifiable queries by retrieving information strictly from official public sources such as Asset Management Company (AMC) websites, AMFI, and SEBI. 

## Core Objective
Design a lightweight assistant that provides concise, source-backed responses to factual queries about mutual funds, while strictly avoiding any investment advice, opinions, or recommendations.

## Target Audience
- Retail investors comparing mutual fund schemes.
- Customer support and content teams handling repetitive queries.

## Key Features & Constraints
- **Facts-Only Responses:** Answers objective questions (e.g., expense ratios, exit loads, SIP amounts, riskometer, lock-in periods) without providing opinions or calculating returns.
- **Source Constraints:** Uses only official public URLs (factsheets, KIM, SID, AMC/AMFI/SEBI FAQs). Strictly no third-party blogs or aggregator websites.
- **Response Formatting Rules:**
  - Maximum of **3 sentences** per response.
  - Exactly **one citation link** per response.
  - Footer required: *"Last updated from sources: <date>"*
- **Refusal Handling:** Must politely refuse non-factual or advisory queries (e.g., "Should I invest in this fund?" or "Which fund is better?") and provide a relevant educational link instead.
- **Data Privacy:** Strict zero-collection policy for PII (PAN, Aadhaar, Account numbers, OTPs, emails, phone numbers).

## Minimal User Interface
- A welcome message.
- Three example questions.
- A permanent, visible disclaimer: **"Facts-only. No investment advice."**

## Scope of Work
- **Corpus Definition:**
  - **AMC:** Aditya Birla Sun Life
  - **Selected Schemes:**
    1. [Birla Sun Life Cash Plus Direct Growth](https://groww.in/mutual-funds/birla-sun-life-cash-plus-direct-growth)
    2. [Birla Sun Life New Millennium Direct Growth](https://groww.in/mutual-funds/birla-sun-life-new-millennium-direct-growth)
    3. [Aditya Birla Sun Life Large Cap Direct Fund Growth](https://groww.in/mutual-funds/aditya-birla-sun-life-large-cap-direct-fund-growth)
    4. [Aditya Birla Sun Life Nifty Midcap 150 Index Fund Direct Growth](https://groww.in/mutual-funds/aditya-birla-sun-life-nifty-midcap-150-index-fund-direct-growth)
    5. [Birla Sun Life Small Midcap Fund Direct Growth](https://groww.in/mutual-funds/birla-sun-life-small-midcap-fund-direct-growth)
  - Curate 15-25 official URLs from the AMC for these schemes to serve as the RAG knowledge base.
- **Deliverables:** 
  1. Complete source code for the RAG assistant and minimal UI.
  2. README document with setup instructions, selected AMC/schemes, architecture overview, and known limitations.
  3. Implementation of the mandatory disclaimer snippet.

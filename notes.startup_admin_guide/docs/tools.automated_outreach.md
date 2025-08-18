# Automated Outreach Pipeline
## Why is this required?

- It can be useful for reaching out to
  - VCs and investors
  - Customers
  - Employees
  - Expand your network

## The Automated Solution

Our pipeline stitches together LinkedIn scraping, email validation, and campaign management into one flow:

**LinkedIn → PhantomBuster → Email Validation → Campaign Launch**

### Core Components

**PhantomBuster**: Your LinkedIn scraping engine
- Connects to Sales Navigator searches
- Pulls profile data automatically (no manual clicking)
- Exports to structured data you can actually use
- Handles rate limits so you don't get banned

**Hunter.io + DropContact**: The email-finding duo
- Hunter.io: Finds emails using name + company domain
- DropContact: Finds emails using just first/last name + company
- Both verify email validity before you send
- Combined approach catches 80%+ of valid emails

**YAMM (Yet Another Mail Merge)**: Google Sheets email automation
- Sends personalized emails directly from Google Sheets
- Tracks opens, clicks, and responses automatically
- Handles unsubscribes and bounces
- No need for expensive email platforms

**Google Sheets**: The control center
- Every step creates a new tab (search → filtered → emails → campaign)
- Easy to review data at each stage
- Non-technical team members can see progress
- Built-in version control for different campaigns

### The Flow

1. **Target Definition**: Define your audience (VCs, customers, partners, employees, etc.)
2. **LinkedIn Extraction**: Use Sales Navigator templates to pull relevant profiles
3. **Profile Filtering**: Remove irrelevant contacts, keep only decision makers
4. **Email Discovery**: Run profiles through Hunter.io and DropContact
5. **Email Validation**: Filter out dead/invalid emails
6. **Campaign Launch**: Send personalized messages via YAMM

### What You Get

- 20-50 verified contacts per target organization
- Automated email validation (no bounces to hurt your domain)
- Campaign tracking and response monitoring
- Scalable process that works across any industry or role

## Data Sources We Tap

Beyond LinkedIn, we pull from:

- **Tracxn**: Company data and investment patterns
  - Scrapes VC firm search results and portfolio companies
  - Extracts investor names, funding rounds, and sectors
  - Downloads as .mhtml files to bypass rate limiting
  - Provides investment history and decision-maker contacts

- **Signal NFX**: Investor lists by stage and vertical
  - Curated lists of investors for different stages (pre-seed, seed, Series A)
  - Organized by vertical (AI, fintech, healthcare, etc.)
  - Extracts investor names and firm data from paginated lists
  - Handles dynamic loading to capture complete datasets

- **FolkApp**: Professional profile data
  - Scrapes shared VC databases using Playwright automation
  - Handles virtualized tables with dynamic row loading
  - Extracts profile data, companies, and contact information
  - Processes structured data into clean CSV formats

- **Industry databases**: Specialized prospect sources
  - **Money2020**: Conference attendee data with authenticated API access
  - **Growjo**: Fastest-growing companies by industry with revenue/funding data
  - **Datamation**: AI company listings with headquarters and revenue details
  - **50pros.com**: Fortune 500 company data including CEOs and key personnel

**Manual sources**: Curated and verified data
- Internal Google Sheets with verified contact information
- Conference attendee lists from industry events
- Manually researched and validated prospect databases
- Team-contributed contact lists with quality control

## Use Cases

- **Fundraising**: Find VCs, angels, and partners at target funds
- **Sales**: Identify decision makers at target companies
- **Hiring**: Source candidates with specific skill sets
- **Partnerships**: Connect with business development teams
- **Customer research**: Reach users in your target segments

## The Technical Reality

This isn't plug-and-play. You need:
- API keys for each service
- Google Sheets integration
- Jupyter notebooks for customization
- Data cleaning functions for each vertical

**Bottom line**: Manual outreach doesn't scale. Automation does. Build the pipeline once, run it forever.

## Why This Matters

Without systematic outreach, you're relying on warm intros and luck. With it, you can test messaging, track response rates, and iterate fast. The difference between 10 conversations and 100 conversations is the difference between hoping someone will respond and having evidence that they will.

# SaaS Boilerplate

## Table of Contents

- [About the project](#about-the-project)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Contact](#contact)


## About The Project
I built a **boilerplate for saas** focused on authentication and integration with **paypal** for payments.
Technologies used:
- **Python** + Django Rest Framework on the backend
- **Javascript** + Typescript + React + Tailwind (Shadcn) on the frontend

For authentication use **JWT** tokens, **OTP** codes for email verification and **SMS** validation (to minimize the use of multiple accounts).

A very simple user flow:
- Registration with email.
- Gift tokens for sms verified users.


## Getting Started
### Prerequisites

### Installation

Project installation steps.

1. git clone https://github.com/francojalil/saas-boilerplate.git
2. cd /saas-boilerplate
3. cd /frontend
4. npm i
5. configure envs variables (backend & frontend)

## Environment Variables
### Backend

#### Google Auth
- [Get Google Cloud Credentials](https://console.cloud.google.com/apis/credentials)
  - `GOOGLE_CLIENT_ID`
  - `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`
  - `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`

#### Twilio SMS
- [Get Twilio Credentials](https://www.twilio.com)
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_VERIFY_SID`

### Frontend

#### Project
- `VITE_URL_BASE`

#### Google Auth
- `VITE_GOOGLE_CLIENT_ID`

#### Paypal
- `VITE_PAYPAL_CLIENT_ID`
- `VITE_PAYPAL_PRODUCT_ID` 

> (Create Paypal Product first in: http://localhost:8000/admin/paypal/paypalproductmodel/)

## Contact

e-mail: francojalil99@gmail.com

linkedin: https://www.linkedin.com/in/franco-jalil/

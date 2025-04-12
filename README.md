## Setup

Check before if pdm is installed.

On MacOS do

`brew install pdm`

1. Clone the repo

2. Backend:

   - `cd bsackend`
   - `pdm install`
   - `pdm run uvicorn app.main:app --reload`

3. Frontend:

   - `npm install`
   - `npm start`

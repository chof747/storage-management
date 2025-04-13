# Template project for FastAPI/React webapps

This is a template project for my FastAPI and React webapps.

It has the following components:

- FastAPI backend service with SQLLite integration (via SQLAlchemy)
- React Frontend with vite containing standard components for
  - sliding forms
  - Filtered Tables allowing viewing, editing and deletion of data
  - A default page for a one entity
  - A menu bar on the side
  - A dashboard page with tiles

This template will be extended on the go.

## How to use it

1. Create a new repository in GitHub and use this repository as the template
2. Clone the new repo locally
3. Start modifying it to your needs

## How to contribute back

Contributing back is by **Todo: Edit this**

## Local Setup

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

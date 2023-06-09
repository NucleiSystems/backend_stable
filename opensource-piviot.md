# what was the original plan

The main mission i was trying to solve, the main reason all of this started out is due to me having a dirty desktop. It pointed out how much clutter we store just incase we need it one day. Nuclei aimed at providing users a limbo-zone for thier files so they can sustain thier files that dont have too much importance in a secure limbozone.

# how is this achived

IPFS is the main workhorse that allows this to work. IPFS is the magical tale of splitting files up and storing them into seperate computers. Peer to peer storage has been highly sought out to reach a more simplified and easy access to produce a peer to peer storage solution. And thats exactly how this application works. Nuclei is built on top of ipfs allowing users to securely ride the peer to peer bus to secure limbo storage.

# Tech stack choices

i will explain in a linear manner on the choices taken to write this app. The main aspiration is to allow users to view thier files wherever they are, whatever device they're on.

To power the backend, we use FastAPI to write the backend.

Python: Python is a very powerful language and due to its simplistic DX it was a simple choice. Python is inheritly "slow" but when paired with uvicorn and a framework which is built on top of the extrememly fast Starlette library.

Postgresql: To store user data, we cannot allow users to depend on local file stores, therefore we use a more elegant solution, with that in mind, the database used is Postgresql, its a simple choice, i didnt use sqlite due to physical database access and saw that as a challange to the security philosophy in mind.

Redis: To allow users to view thier files, we fetch user's data with an internal routine that assembles a request to securely collect user's files and systematically audit user's files. Per view, user's files are fetched, however, to avoid having to fetch everytime, we use Redis to cache thier files in memory (**THIS NEED IMMEDIATE REWORK FOR CLIENT, store the files temporarily on the client with encrypted sharding).** For web and mobile platforms, redis is a simplistic solution for web-based caching of user's file byte data.

# Nuclei

built using Fastapi and flutter and respective extensions.

Nuclei is a web application that allows you to upload and manage your own compressed media to increase media availability and accessibility.

Nuclei Daemon Moderans for Linux is an open source software that securely stores your media files using IPFS (InterPlanetary File System) with compression applied to decrease the size of the media files. It provides temporary access to the files to increase the security of the media.

I'm currently looking for contributors who are passionate about building user-friendly applications that prioritize privacy and security.

Some of the expectations for contributors include having experience with Python and FastAPI, as well as a good understanding of SQL databases such as PostgreSQL. Additionally, I'm looking for individuals who share a similar philosophy to mine when it comes to the functionality of the application, such as utilizing IPFS for decentralized storage and implementing end-to-end encryption to ensure user privacy.

If you're interested in contributing to the project, please feel free to reach out to me. Let's work together to build a better, more secure future for data storage.

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

# Mission

The mission of Nuclei is to provide a secure and efficient way to store and access media files. By leveraging the power of IPFS and compression techniques, Nuclei aims to provide a solution that not only reduces the size of the files but also ensures the files are stored securely.

# Problems solved by Nuclei

- Security: Nuclei provides a secure way to store media files by using IPFS. The files are encrypted and can only be accessed by users with the appropriate permissions.
- Efficiency: By applying compression techniques, Nuclei reduces the size of media files, making it faster and more efficient to store and access them.
- Accessibility: Nuclei provides temporary access to media files, making it more secure by limiting the time a file is accessible.
  How to run
  Nuclei can be run using Docker Compose. Here are the steps to get started:

# Clone the repository:

bash

- Copy code
- git clone https://github.com/Nuclei-Media/daemon-moderans-linux.git
- use docker-compose up to run the application

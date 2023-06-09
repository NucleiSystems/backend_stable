# How to contribute

Thank you for considering contributing to Nuclei! We're excited to have you here and would love for you to join our community of contributors.

## Resources

Here are some resources that might be helpful:

* [Flask Tutorials](https://realpython.com/tutorials/flask/): If you're new to Flask or want to learn more about it, we recommend checking out these tutorials.
* [FastAPI Tutorials](https://fastapi.tiangolo.com/tutorial/): FastAPI is the framework we use to build Nuclei's backend API. If you're not familiar with it, these tutorials are a great place to start.
* [Docker Tutorials](https://www.docker.com/101-tutorial): Docker is used to containerize and deploy Nuclei. If you're not familiar with Docker, we recommend checking out these tutorials.
* [Redis Tutorials](https://redis.io/documentation): Redis is used to cache files and improve performance. If you're not familiar with Redis, we recommend checking out their official documentation.
* [PostgreSQL Tutorials](https://www.postgresqltutorial.com/): PostgreSQL is used to store metadata about files. If you're not familiar with PostgreSQL, we recommend checking out these tutorials.
* [Python Tutorials](https://www.learnpython.org/): If you're not familiar with Python, we recommend checking out these tutorials.

* [Discord](https://discord.gg/Ss6Tu4BD). Core Contributors will usually answer questions out of thier own volition, otherwise other users will be available for help.

## Submitting changes

If you've made some changes to Nuclei and would like to contribute them, here's how to do it:

1. Fork the repository and create a new branch.
2. Make your changes and write tests for them.
3. Make sure the tests pass by running `pytest` in the root directory of the project.
4. Commit your changes and push your branch to your fork of the repository.
5. Open a pull request to the Nuclei repository and describe your changes.


## Coding conventions

Start reading our code and you'll get the hang of it. We optimize for readability and latest conventions to support and accommodate PEPs:

* We indent using Tabs (no spaces please)
* We use Black Formatter where ever necessary (please ensure your code is formatted)
* View files need to be deviated from the logic which is being applied from data requested
  * if a view is handling data, design seperate scoped functions/classes to handle data
  * Python and fastapi operations are seperated to maximise readability and debuggability
  * avoid cluttering view routes with exceptions
* Current File Structure is concrete and wont be facing changes anytime soon
* Tests arent nessisary, however, if written and failed, pull request will be denied
* Perfect pull requests arent a requirement, logic improvements are always appreciated
* Assure code follows PEP8 rulesets, however to iterate again, its not an requirement, the requirement is to format the python code.

Thank you for taking the time to read this and considering contributing to Nuclei. If you have any questions or need help, please don't hesitate to reach out to us on [Discord](https://discord.gg/Ss6Tu4BD). We're happy to help and look forward to your contributions! We value all contributions and are grateful for your help in making this app the best it can be. If you have any questions or concerns, please feel free to reach out to us on Discord or through a GitHub issue. Happy coding!

Best regards,

Rohaan Ahmed, Core Developer - Nuclei



<!-- toc -->

- [DATA605 Class Projects](#data605-class-projects)
  * [Choosing a project](#choosing-a-project)
  * [Pre-requisites](#pre-requisites)
  * [Working on the project](#working-on-the-project)
    + [Contribution to the repo](#contribution-to-the-repo)
    + [Documentation](#documentation)
  * [Submission](#submission)
  * [Examples of a class project](#examples-of-a-class-project)

<!-- tocstop -->

# DATA605 Class Projects

- The goal of the class project is to learn cutting-edge modern big data
  technology and write a (small) example of a system using it
- Each class project is similar in spirit to the tutorials for various
  technologies (e.g., Git, Docker, SQL, Mongo, Airflow, Dask) we have looked at
  and studied in classes
- Through the class projects you will learn how a tool will fit your
  Datascience/Data engineering/Machine Learning workflows.

## Choosing a project

- Each student should pick one of the projects from the
  [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0)
  - The difficulty of the project does affect the final grade, but we want to
    give a way for everyone to select a project based on their level of computer
    literacy
  - Each project has a description in the
    [Google Doc](https://docs.google.com/document/d/1fEd7_oLhFnA5ovzj_HMb9EeMU84nOGEGeWqNRZSz2wo)
    under a header with the same name of the Project Name
  - You need to fill out the yellow fields in the
    [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0),
    such as Name, GitHub user, UMD ID, GitHub issue, Date. Once done, we will
    add you to the repo so that you can start working

- The project is individual
  - Students can discuss and help each other (they will do that even if we say
    not to)
  - Students should not have exactly the same project
  - If there are no more projects left for any reason, let us know and we will
    add more.

- The goal is to get your hands dirty and figure things out
  - Often working is all about trying different approaches until one works out
  - Make sure you code by understanding the tool and what your code doing with
    it
  - Google and ChatGPT are your friends, but don't abuse them: copy-pasting code
    is not recommmended and won't benefit the learning outcomes. The projects
    are designed in a way that once you understand the underlying technology:
    - Easy Project: Takes 2-3 days to complete
    - Medium Difficulty Project: Takes 4-5 to complete
    - Difficult Project: Takes 6-8 to complete.

- It is highly recommended to choose a project from the
  [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0).
  If you'd like to propose a new idea or suggest modifications, please contact
  us—we will review and accommodate reasonable requests.
- Your project should align with your learning goals and interests, offering a
  great opportunity to explore various technologies and strengthen your resume.
- If selecting a project from the sign-up sheet, ensure you fill out the
  corresponding details promptly. For modifications, email us with the necessary
  information, and we will update the sign-up sheet and Google Doc accordingly.
- **Project selection must be finalized within one week** to allow sufficient
  time for planning and execution.
- The project duration is approximately **four weeks**, making timely selection
  crucial.
- Your grade will be based on **project complexity, effort, understanding, and
  adherence to guidelines**.

**NOTE**:

- If you choose use a paid service, you are responsible for the costs incurred.
  You are expected to use the services efficiently to keep them within free tier
  usage
- To save costs/improve usage, you should make sure that the services are turned
  off/shutdown when not being used.

## Pre-requisites

- Watch, star, and fork the Causify.AI repo
- Install Docker on your computer
  - Ok to use Docker natively on Mac and Linux
  - Use VMware in Windows or dual-boot
    - If you have problems installing it on your laptop, it recommended to use
      one computer from UMD, or perhaps a device of one your friends
- After signing up for a project accept the invitation to collaborate sent to
  the email that you used to register your GitHub account, or check
  [here](https://github.com/causify-ai/tutorials/invitations)
- Check your GitHub issue on https://github.com/causify-ai/tutorials/issues
  - Make sure you are assigned to it
- Only Python should be used together with the needed configs for the specific
  tools
  - You can always communicate with the tech using Python libraries or HTTP APIs

- Unless specified by project description, everything needs to run locally
  without using cloud resources.
  - E.g., it's not ok to use an AWS DB instance, you want to install Postgres in
    your container

## Working on the project

### Contribution to the repo

- You will work in the same way open-source developers (and specifically
  developers on Causify.AI) contribute to a project

- Setup your working environment by following the instructions in the
  [document](https://github.com/causify-ai/helpers/blob/master/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

- Each step of the project is delivered by committing code to the dir
  corresponding to your project and doing a GitHub Pull Request (PR)
  - You should commit regularly and not just once at the end
  - We will specifically do a reviews of intermediate results of the project and
    give you some feedback on what to improve (adopting Agile methodology)

- Each project will need to be organized like a proper open source project,
  including filing issues, opening PRs, checking in the code in
  https://github.com/causify-ai/tutorials

- The tag of your projects follows the schema
  `Spring{year}_{project_title_without_spaces}`
  - E.g., if the project title is "`Redis cache to fetch user profiles`", the
    tag is `Spring2025_Redis_cache_to_fetch_user_profiles`

- Create a GitHub issue with the project tag as title (e.g.,
  `Spring2025_Redis_cache_to_fetch_user_profiles`) and assign the issue to
  yourself
  - Copy/paste the description of the project and add a link to the Google doc
    with the description
  - We will use this issue to communicate as the project progresses

- Create a branch in Git named after your project
  - E.g., `TutorialsTask645_Redis_cache_to_fetch_user_profiles` where 645 is the
    git hub issue number.
  ```
  > cd $HOME/src
  > git clone git@github.com:causify-ai/tutorials.git tutorials1
  > cd $HOME/src/tutorials1
  > git checkout master
  > git checkout -b TutorialsTask645_Redis_cache_to_fetch_user_profiles
  ...
  ```

- You should add files only under the directory corresponding to your project
  which is like `{GIT_ROOT}/sandbox/projects/{project_tag}`
  - E.g., on the dir cloned on my laptop the dir is named
    `~/src/tutorials1/sandbox/projects/TutorialsTask645_Redis_cache_to_fetch_user_profiles`

- You always need to create a PR from your branch and add `@tkpratardan`,
  `@Prahar08modi`, `@gpsaggese` as reviewers
  - Remember that you can't push directly to `master` branch
  - You should only push the commits in the branch specific to your project

- You should use consecutive branch and PR names as you make progress
  - E.g., `TutorialsTask645_Redis_cache_to_fetch_user_profiles_1`,
    `TutorialsTask645_Redis_cache_to_fetch_user_profiles_2`, ...

### Documentation

For your course project, you're not just building something cool—you're also
teaching others how to use a Big Data, AI, LLM, or data science tech. Instead of
a project report, you'll create a tutorial that's hands-on and
beginner-friendly. Think of it as your chance to help a classmate get started
with the same tech. The goal of this tutorial help pickup a new technology in 60
Minutes! That should make sure the tutorial is not lengthy and covers all the
important aspects a developer should know before

You are expected to create an end-to-end tutorial for your package in accordance
with the guidelines mentioned
[here](https://github.com/causify-ai/tutorials/blob/f0f37d83919d552fabb0505240d016b4b7028ca3/docs/all.how_write_tutorials.how_to_guide.md):

## Submission

- You will submit two markdown files
* `XYZ.API.md`: A markdown about the API and the software layer written by
  you on top of the native API
* `XYZ.example.md`: A markdown with a full example of an application using
  the API
  - At least 1 page (60 lines): explain how to run the system by starting the
    container system, e.g.,
    - Report command lines
    - How the output looks like
    - ...
  - At least 3 pages (60 lines): describe exactly what you have done
    - Describe the script/notebook with examples of the output
    - Use diagrams (e.g., use `mermaid`)
    - Describe the schema used in the DB if you have any
    - ...

- The script/notebook should be able to run end-to-end without errors, otherwise
  the project is not considered complete Idelly the notebook should run
  correctly by executing "Restart and Run all cells" before a commit is pushed.
  - We are not going to debug your code
  - If there are problems we will use the GitHub issue to communicate and we
    expect you to fix the problem

**NOTE**: The Markdown files should not be copy-paste of the notebook's cells
and output.

## Examples of a class project

- The layout of each project should follow the example in
  https://github.com/causify-ai/tutorials/tree/master/tutorial_asana
- Examples for neo4j in
  https://github.com/causify-ai/tutorials/tree/master/tutorial_neo4j
- The tutorials from DATA605 class

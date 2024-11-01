# Contributing to BurnOut 5.0
<h3>Hello!👋</h3>
<p>Firstly, thank you so much for showing interest in BurnOut 5.0 and contributing to our project.👍</p>
The following are a set of guidelines for contributing to BurnOut. We are open to suggestions to enhance our project so feel free to propose changes to this document in a pull request.


### Table of contents
[Code of Conduct](#code-of-conduct)

[How Can I Contribute?](#how-can-i-contribute)
 * [Reporting Bugs](#reporting-bugs)
 * [Suggesting enhancements](#suggesting-enhancements)
 * [Submitting a pull request](#submitting-a-pull-request)

[Style Guides](#style-guides)

[Need additional help?](#need-additional-help)

[References](#references)


### Code of Conduct
Everyone participating in this project needs to abide by the aPAS - A Personal Agile Scheduler Code of Conduct that can be found under the main repository link as a CODE_OF_CONDUCT.md file. By participating, you are expected to uphold this code. Please report unacceptable behavior to any of the original team members listed at the bottom of [README.md](README.md).

## How Can I Contribute?


  ## Reporting Bugs

  This section guides you through submitting a bug report for SE Group 53 of Fall 2023. 

  When you are creating a bug report, please ensure that you include as many details as possible to understand the issue.

  ## How Do I Submit A Bug Report?
   <p>Bugs are tracked as GitHub issues. After you've determined which repository your bug is related to, create an issue on that repository.
    Explain the problem and include additional details to help maintainers reproduce the problem:</p>
   <ul>
    <li><b>Use a clear and descriptive title</b> for the issue to identify the problem.</li>
    <li><b>Describe the exact steps which reproduce the problem in as many details as possible.</li></b>
    <li><b>Provide specific examples to demonstrate the steps.</b> Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those     examples. If you're providing snippets in the issue, use Markdown code blocks.</li>
    <li><b>If the problem is related to performance or memory, then ensure that you include a CPU profile capture with your report.</b></li>
    <li><b>Include screenshots and animated GIFs which show you following the described steps and clearly demonstrate the problem.</li></b>
    <li><b>If the problem wasn't triggered by a specific action</b>, describe what you were doing before the problem happened and share more information using the guidelines below.</li>
    </ul>
  
  ## Suggesting Enhancements
  This section guides you through submitting a suggestion for BurnOut, including completely new features and minor improvements to existing functionality. 

  Enhancement suggestions are tracked as GitHub issues. 
  After you've determined which repository your enhancement suggestion is related to, create an issue on that repository and provide the information like title, step-by-step description, specific examples.\
  Giving more detailed information will help us understand the suggestion better. 
  
  #### Provide details like 
  1) What is the enhancement? 
  2) Suggestions to implement the enhancement

  ## Submitting a pull request

1. [Fork][fork] and clone the repository.
1. Configure and install the dependencies: `npm install`.
1. Make sure the tests pass on your machine: `npm test`, note: these tests also apply the linter, so there's no need to lint separately.
1. Create a new branch: `git checkout -b my-branch-name`.
1. Make your change, add tests, and make sure the tests still pass.
1. Push to your fork and [submit a pull request][pr].
1. Pat your self on the back and wait for your pull request to be reviewed and merged.

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

- Follow the [style guide][style] which is using standard. Any linting errors should be shown when running `npm test`.
- Write and update tests.
- Keep your changes as focused as possible. If there are multiple changes you would like to make that are not dependent upon each other, consider submitting them as separate pull requests.
- Write a [good commit message](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).

Work in Progress pull requests are also welcome to get feedback early on, or if there is something blocked you.

### <h2>Style Guides</h2>

#### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* When only changing documentation, include `[ci skip]` in the commit title


#### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Reference methods and classes in markdown with the custom `{}` notation:
    * Reference classes with `{ClassName}`
    * Reference instance methods with `{ClassName::methodName}`
    * Reference class methods with `{ClassName.methodName}`


## Git Commit Messages

  - Describe why any particular modification is being made.

  - Give a detailed description about the limitations of current code.

  - Use the imperative mood ("Move cursor to..." not "Moves cursor to...")

  - Limit the first line to 72 characters or less

  - Link an issue to the change

## Python Style Guides :

  All Python code is linted with Pylint. Ensure that before you commit any changes, your code passes all the default pylint checks. Pylint can be installed with
  `pip install pylint`.


### <h2>Need Additional Help?</h2>
<p>Due to any reason, if you feel like you have reservations related to the process, feel free to reach us out at [burnoutapp2023@gmail.com] Github process can be a bit complex and we don't want to lose your valuable contributions because of that reason. We are extremely glad that you have visited us and will make our project much better.</p>


## References
[Contributing.md](https://github.com/atom/atom/blob/master/CONTRIBUTING.md#specs-styleguide)

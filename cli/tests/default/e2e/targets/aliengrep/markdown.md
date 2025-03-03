<p align="center">
    <a href="https://fastlint.dev"><img src="fastlint.svg" height="100" alt="Fastlint logo"/></a>
</p>
<h3 align="center">
  Lightweight static analysis for many languages.
  </br>
  Find and block bug variants with rules that look like source code.
</h3>

<p align="center">
  <a href="#getting-started">Getting Started</a>
  <span> · </span>
  <a href="#Examples">Examples</a>
  <span> · </span>
  <a href="#resources">Resources</a>
  <br/>
  <a href="#usage">Usage</a>
  <span> · </span>
  <a href="#contributing">Contributing</a>
  <span> · </span>
  <a href="#commercial-support">Commercial Support</a>
</p>

<p align="center">
  <a href="https://formulae.brew.sh/formula/fastlint">
    <img src="https://img.shields.io/homebrew/v/fastlint?style=flat-square" alt="Homebrew" />
  </a>
  <a href="https://pypi.org/project/fastlint/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/fastlint?style=flat-square&color=blue">
  </a>
  <a href="https://r2c.dev/slack">
    <img src="https://img.shields.io/badge/slack-join-green?style=flat-square" alt="Issues welcome!" />
  </a>
  <a href="https://github.com/khulnasoft/fastlint/issues/new/choose">
    <img src="https://img.shields.io/badge/issues-welcome-green?style=flat-square" alt="Issues welcome!" />
  </a>
  <a href="https://github.com/khulnasoft/fastlint#readme">
    <img src="https://img.shields.io/github/stars/khulnasoft/fastlint?label=GitHub%20Stars&style=flat-square" alt="1500+ GitHub stars" />
  </a>
  <a href="https://twitter.com/intent/follow?screen_name=r2cdev">
    <img src="https://img.shields.io/twitter/follow/r2cdev?label=Follow%20r2cdev&style=social&color=blue" alt="Follow @r2cdev" />
  </a>
</p>

<a href="https://fastlint.dev">Fastlint</a> tl;dr:

- A simple, customizable, and fast static analysis tool for finding bugs
- Combines the speed and customization of `grep` with the precision of traditional static analysis tools
- No painful domain-specific language; Fastlint rules look like the source code you’re targeting
- Batteries included with hundreds of existing community rules for OWASP Top 10 issues and common mistakes
- Runs in CI, at pre-commit, or in the editor
- Runs offline on uncompiled code

Fastlint supports:

| Go  | Java | JavaScript | JSON | Python | Ruby (beta) | JSX (beta) | C (alpha) | OCaml (alpha) |
| --- | ---- | ---------- | ---- | ------ | ----------- | ---------- | --------- | ------------- |


Fastlint is proudly supported by r2c. Learn more about a hosted version of Fastlint with an enterprise feature set at [r2c.dev](https://r2c.dev/).

## Getting Started

The best place to start with Fastlint and rule writing is its [Quick Start](https://fastlint.dev/editor). For a more in-depth introduction to its syntax and use cases visit the [Fastlint Tutorial](https://fastlint.dev/learn).

Fastlint can be installed using `brew`, `pip`, or `docker`:

```sh
# For macOS
$ brew install fastlint

# On Ubuntu/WSL/linux, we recommend installing via `pip`
$ python3 -m pip install fastlint

# To try Fastlint without installation run via Docker
$ docker run --rm -v "${PWD}:/src" khulnasoft/fastlint --help
```

To confirm installation and get an overview of Fastlint's functionality run with `--help`:

```
$ fastlint --help
```

Once installed, Fastlint can be run with single rule patterns or entire rule sets:

```sh
# Check for Python == where the left and right hand sides are the same (often a bug)
$ fastlint -e '$X == $X' --lang=py path/to/src

# Run a ruleset with rules for many languages
$ fastlint --config=https://fastlint.dev/p/r2c-CI path/to/src
```

Explore the Fastlint Registry of rules and CI integrations at [fastlint.dev](https://fastlint.dev/packs).

## Examples

| Use case                          | Fastlint rule                                                                                                                                                                                                                                                                                                                                           |
| :-------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ban dangerous APIs                | [Prevent use of exec](https://fastlint.live/clintgibler:no-exec)                                                                                                                                                                                                                                                                                        |
| Search routes and authentiation   | [Extract Spring routes](https://fastlint.live/clintgibler:spring-routes)                                                                                                                                                                                                                                                                                |
| Enforce the use secure defaults   | [Securely set Flask cookies](https://fastlint.dev/dlukeomalley:flask-set-cookie)                                                                                                                                                                                                                                                                        |
| Enforce project best-practices    | [Use assertEqual for == checks](https://fastlint.dev/dlukeomalley:use-assertEqual-for-equality), [Always check subprocess calls](https://fastlint.dev/dlukeomalley:unchecked-subprocess-call)                                                                                                                                                            |
| Codify project-specific knowledge | [Verify transactions before making them](https://fastlint.dev/dlukeomalley:verify-before-make)                                                                                                                                                                                                                                                          |
| Audit security hotspots           | [Finding XSS in Apache Airflow](https://fastlint.live/ievans:airflow-xss), [Hardcoded credentials](https://fastlint.dev/dlukeomalley:hardcoded-credentials)                                                                                                                                                                                              |
| Audit configuration files         | [Find S3 ARN uses](https://fastlint.dev/dlukeomalley:s3-arn-use)                                                                                                                                                                                                                                                                                        |
| Migrate from deprecated APIs      | [DES is deprecated](https://fastlint.dev/editor?registry=java.lang.security.audit.crypto.des-is-deprecated), [Deprecated Flask APIs](https://fastlint.dev/editor?registry=python.flask.maintainability.deprecated.deprecated-apis), [Deprecated Bokeh APIs](https://fastlint.dev/editor?registry=python.bokeh.maintainability.deprecated.deprecated_apis) |
| Apply automatic fixes             | [Use listenAndServeTLS](https://fastlint.live/clintgibler:use-listenAndServeTLS)                                                                                                                                                                                                                                                                        |

### Try it out

Give some rulesets a spin by running on known vulnerable repositories:

```bash
# juice-shop, a vulnerable Node.js + Express app
$ git clone https://github.com/bkimminich/juice-shop
$ fastlint -f https://fastlint.dev/p/r2c-security-audit juice-shop
```

```bash
# railsgoat, a vulnerable Ruby on Rails app
$ git clone https://github.com/OWASP/railsgoat
$ fastlint -f https://fastlint.dev/p/r2c-security-audit railsgoat
```

```bash
# govwa, a vulnerable Go app
$ git clone https://github.com/0c34/govwa
$ fastlint -f https://fastlint.dev/p/r2c-security-audit govwa
```

```bash
# vulnerable Python+Flask app
$ git clone https://github.com/we45/Vulnerable-Flask-App
$ fastlint -f https://fastlint.dev/p/r2c-security-audit Vulnerable-Flask-App
```

```bash
# WebGoat, a vulnerable Java+Sprint app
$ git clone https://github.com/WebGoat/WebGoat
$ fastlint -f https://fastlint.dev/p/r2c-security-audit WebGoat
```

## Resources

Learn more:

- [Live Editor](https://fastlint.dev/editor)
- [Fastlint Registry](https://fastlint.dev/r)
- [Documentation](docs/README.md)
- [r2c YouTube channel](https://www.youtube.com/channel/UC5ahcFBorwzUTqPipFhjkWg)

Get in touch:

- Submit a [bug report](https://github.com/khulnasoft/fastlint/issues)
- Join the [Fastlint Slack](https://r2c.dev/slack) to say "hi" or ask questions

## Usage

### Command Line Options

See `fastlint --help` for command line options.

### Exit Codes

`fastlint` may exit with the following exit codes:

- `0`: Fastlint ran successfully and found no errors
- `1`: Fastlint ran successfully and found issues in your code
- \>=`2`: Fastlint failed to run

### Upgrading

To upgrade, run the command below associated with how you installed Fastlint:

```sh
# Using Homebrew
$ brew upgrade fastlint

# Using pip
$ python3 -m pip install --upgrade fastlint

# Using Docker
$ docker pull khulnasoft/fastlint:latest
```

## Contributing

Fastlint is LGPL-licensed and we welcome contributions.

To start contributing, first please make sure you read and agree with the [Contributor Covenant Code of Conduct](https://github.com/khulnasoft/fastlint/blob/develop/CODE_OF_CONDUCT.md).
Then check out a few ways you can get involved:

- [File an issue](https://github.com/khulnasoft/fastlint/issues/new/choose)
- Fix a bug — pick from the [good first issues](https://github.com/khulnasoft/fastlint/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) or work on any of the [currently open bugs](https://github.com/khulnasoft/fastlint/issues?q=is%3Aopen+is%3Aissue+label%3Abug)
- Add a feature — see the [enhancement issues](https://github.com/khulnasoft/fastlint/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement) for inspiration
- Update the [docs](https://github.com/khulnasoft/fastlint/tree/develop/docs)
- Help each other in the [community Slack](https://r2c.dev/slack)

Please see the [contribution guidelines](https://github.com/khulnasoft/fastlint/blob/develop/doc/README.md) for info about the development workflow, testing, and making PRs.

## Commercial Support

Fastlint is a frontend to a larger program analysis library named [`pfff`](https://github.com/khulnasoft/pfff/). `pfff` began and was open-sourced at [Facebook](https://github.com/facebookarchive/pfff) but is now archived. The primary maintainer now works at [r2c](https://r2c.dev). Fastlint was originally named `sgrep` and was renamed to avoid collisons with existing projects.

Fastlint is supported by [r2c](https://r2c.dev). We're hiring!

Interested in a fully-supported, hosted version of Fastlint? [Drop your email](https://forms.gle/dpUUvSo1WtELL8DW6) and we'll be in touch!

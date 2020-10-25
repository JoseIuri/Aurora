# XGeneratorTB Automatic Testbench Creator

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Running the tests](#running-the-tests)
- [Authors](#authors)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Getting Started

Implements an Automatic testbench creator based on Python and template files. This software automatize the connections between the UVM Componnents in the environment based on a configuration as a input for code generation.

### Prerequisites

```
Python 3.X

Packages:
    os
    sys
    getopt
    colorama
    pathlib
```

## Running the tests

To run the software use this command line from rundir folder:

```
python3 ../scripts/xgtb.py -i <input_configuration_file> -o <output-directory>
```


## Authors

* **José Iuri Barbosa de Brito** - [JoseIuri](https://github.com/JoseIuri)

See also the list of [contributors](https://github.com/JoseIuri/XGeneratorTB/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Contributing

1. Fork it (<https://github.com/JoseIuri/Simple_UVM/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Acknowledgments

* XMEN Lab - Federal University of Campina Grande - Brazil

<p align="center">
  <a href="https://www.embedded.ufcg.edu.br/">
    <img alt="XMEN Lab" title="XMEN Lab" src="https://i.imgur.com/IzbZM0E.png" width="200">
  </a>
</p>

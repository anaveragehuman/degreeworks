# degreeworks

Scraper for [Ellucian Degree Works](https://www.ellucian.com/solutions/ellucian-degree-works)

## Usage

1. Navigate to Degree Works and save a local copy of the page.

1. Run [main.py](main.py) with the index page as an argument.
   Use `-h` to see all valid arguments.

    ```sh
    $ ./main.py -qr 3 degreeworks.html
    ENGL 25080
    ENGL 25092
    ENGL 25096
    WGSL 29003
    ```

1. Profit!

## Dependencies

Requires at least Python 3.6 and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/).

## Bugs

Likely many, as this was only tested with one Degree Works profile.
Based on an unstable API; what works today may not work tomorrow.

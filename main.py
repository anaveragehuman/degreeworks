#!/usr/bin/env python3

import re
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from collections import defaultdict, namedtuple
from os.path import realpath
from typing import Dict, Set, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

COURSE_RE = re.compile("javascript:GetCourseInfo\('(.+?)','(.+?)'\)")
Course = namedtuple("Course", ["dept", "num"])


def parse_js(string: str) -> Course:
    match = COURSE_RE.match(string)
    return Course(*match.group(1, 2)) if match is not None else None


def get_reqs(soup: BeautifulSoup) -> Tuple[Dict[Course, str], Dict[str, Set[str]]]:
    trs = soup.find_all("tr", attrs={"class": "bgLight0"})  # red

    courses: Dict[str, str] = {}  # code, description
    reqs: Dict[str, Set[str]] = defaultdict(set)  # code, fulfills
    ats: Dict[Course, Set[str]] = defaultdict(set)  # Course, fulfills

    req = None

    for tr in trs:
        req_candidate = tr.find("td", attrs={"class": "RuleLabelTitleNeeded"})

        if req_candidate is not None:
            req = req_candidate.string

        needed_list = tr.find_all("td", attrs={"class": "RuleAdviceData"})

        for needed in needed_list:
            for a in needed.find_all("a"):
                if "href" not in a.attrs:  # TODO link without href is "Except"
                    continue  # ideally schedule for removal

                cc = parse_js(a["href"])
                if cc is None:
                    continue

                if "@" in cc.num or ":" in cc.num:
                    ats[cc].add(req)
                    continue

                reqs[cc].add(req)

                if "title" in a.attrs:  # @ doesn't have titles
                    course_desc = a["title"]
                    courses[cc] = course_desc

    for cc, fulfills in ats.items():  # handle @
        keep = True  # only remove if it matches at least one other

        def add_reqs(course: Course) -> None:
            nonlocal keep

            if course in reqs:
                reqs[course] |= fulfills
                keep = False

        if "@" in cc.num:
            front, back = cc.num.split("@")
            need_digits = 5 - len(front) - len(back)

            for i in range(10 ** need_digits):
                x = str(i)
                pad = need_digits - len(x)
                course = Course(cc.dept, f"{front}{pad * '0'}{x}{back}")
                add_reqs(course)
        elif ":" in cc.num:
            front, back = [int(i) for i in cc.num.split(":")]
            for i in range(front, back + 1):  # needs to be inclusive
                add_reqs(Course(cc.dept, i))

        if keep:
            reqs[cc] = fulfills

    return reqs, courses


def print_dups(
    reqs: Dict[str, Set[str]],
    courses: Dict[Course, str],
    min: int = 2,
    quiet: bool = False,
) -> None:
    for cc, reqlist in sorted(reqs.items()):
        if len(reqlist) >= min:
            cname = courses.get(cc)
            code = f"{cc.dept} {cc.num}"

            if quiet:
                print(code)
            else:
                print(f"{code} - {cname}:" if cname else f"{code}:")

                for req in reqlist:
                    print(f"\t{req}")
                print()


def run(file: str) -> Tuple[Dict[Course, str], Dict[str, Set[str]]]:
    bodysrc = None
    basedir = None

    with open(file) as f:
        basedir = realpath(f.name)
        soup = BeautifulSoup(f, features="lxml")
        bodysrc = soup.find("frame", attrs={"name": "frBodyContainer"})["src"]

    bodysrc2 = None
    with open(urljoin(basedir, bodysrc)) as f:
        basedir = realpath(f.name)
        soup = BeautifulSoup(f, features="lxml")
        bodysrc2 = soup.find("frame", attrs={"name": "frBody"})["src"]

    mainsoup = None
    with open(urljoin(basedir, bodysrc2)) as f:
        mainsoup = BeautifulSoup(f, features="lxml")

    return get_reqs(mainsoup)


def main() -> None:
    p = ArgumentParser(
        description="Parses Ellucian Degree Works to find \
                                    courses that satisfy requirements",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--quiet", "-q", action="store_true", help="show course codes only")
    p.add_argument(
        "--reqs",
        "-r",
        action="store",
        default=2,
        type=int,
        help="minimum number of requirements to satisfy",
    )
    p.add_argument(
        "file",
        default="degreeworks.html",
        nargs="?",
        help="locally saved copy of Degree Works",
    )

    args = p.parse_args()
    reqs, courses = run(args.file)
    print_dups(reqs, courses, args.reqs, args.quiet)


if __name__ == "__main__":
    main()

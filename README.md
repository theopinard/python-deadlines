## Python Deadlines [![pages-build-deployment](https://github.com/JesperDramsch/python-deadlines/actions/workflows/pages/pages-build-deployment/badge.svg?branch=gh-pages)](https://github.com/JesperDramsch/python-deadlines/actions/workflows/pages/pages-build-deployment)

Countdown timers to keep track of a bunch of Python conference deadlines.

## Contributing

Contributions are very welcome!

To add or update a deadline:
- Fork the repository
- Update `_data/conferences.yml`
- Make sure it has the `title`, `year`, `id`, `link`, `cfp`, `timezone`, `date`, `place`, `sub` attributes
    + See available timezone strings [here](https://momentjs.com/timezone/).
- Optionally add a `note`
- Example:
    ```yaml
    - title: BestConf
      year: bestConf22                         # unique ID can be anything within reason
      id: bestconf22                           # title as lower case + last two digits of year
      full_name: Best Conference for Anything  # Full conference name (Optional)
      link: link-to-website.com                # URL to conference
      cfp: YYYY-MM-DD HH:SS                    # Deadline for Call for Participation / Proposals
      workshop_deadline: YYYY-MM-DD HH:SS      # Workshop deadline if different from cfp (Optional)
      tutorial_deadline: YYYY-MM-DD HH:SS      # Tutorial deadline if different from cfp (Optional)
      timezone: Asia/Seoul                     # Standard Timezones
      place: Incheon, South Korea              # City, Country
      date: September, 18-22, 2022             # Nicely written dates of conference
      start: YYYY-MM-DD                        # Start date of conference for calendar
      end: YYYY-MM-DD                          # Start date of conference for calendar
      sub: PY                                  # Type of conference (see or add _data/types.yml)
      note: Important                          # In case there are extra notes about the conference (Optional)
    ```
- Send a pull request

## Forks & other useful listings

- [aideadlines][2] the original
- [geodeadlin.es][3] by @LukasMosser
- [neuro-deadlines][4] by @tbryn
- [ai-challenge-deadlines][5] by @dieg0as
- [CV-oriented ai-deadlines (with an emphasis on medical images)][8] by @duducheng
- [es-deadlines (Embedded Systems, Computer Architecture, and Cyber-physical Systems)][9] by @AlexVonB and @k0nze
- [2019-2020 International Conferences in AI, CV, DM, NLP and Robotics][10] by @JackieTseng
- [ccf-deadlines][11] by @ccfddl
- [netdeadlines.com][12] by @albertgranalcoz
- [ad-deadlines.com][13] by @daniel-bogdoll

## License

This project is licensed under [MIT][1].

It uses:

- [IcoMoon Icons](https://icomoon.io/#icons-icomoon): [GPL](http://www.gnu.org/licenses/gpl.html) / [CC BY4.0](http://creativecommons.org/licenses/by/4.0/)

[1]: https://abhshkdz.mit-license.org/
[2]: http://aideadlin.es/
[3]: https://github.com/LukasMosser/geo-deadlines
[4]: https://github.com/tbryn/neuro-deadlines
[5]: https://github.com/dieg0as/ai-challenge-deadlines
[6]: http://www.conferenceranks.com/#
[8]: https://m3dv.github.io/ai-deadlines/
[9]: https://ekut-es.github.io/es-deadlines/
[10]: https://jackietseng.github.io/conference_call_for_paper/conferences.html
[11]: https://ccfddl.github.io/
[12]: https://netdeadlines.com/
[13]: https://ad-deadlines.com/

## VerbumMalum

List of malicious phishing domains prominently spread through Discord

### Project setup

1. Ensure Python is installed
2. Clone this repository (`git clone ...`)
3. In the repository, create a Python virtual environment (`python -m venv venv`) and activate it (`source venv/bin/activate`)
4. Install this project's requirements (`pip install -r requirements.txt`)

### How to make an entry

1. Run `python make_entry.py MALICIOUS_DOMAIN_HERE`. This will create a path for the domain in `entries/<first letter of domain>/<domain>/`
2. If the URL was spread through an image attachment, and you still have that image, also add the image to the entry folder (titled "image.png"/"image.jpg"/etc.)
3. Create a pull request to add your entry to the main repo.  
   Follow GitHub's tutorial on creating PRs here:
   - [Text form](<https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>)
   - [Video form](<https://youtu.be/nCKdihvneS0>)

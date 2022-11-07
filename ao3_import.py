import import_utility

# If you want to import only works with specific tags, list them below
# Otherwise leave the list empty
MY_TAGS = [110293, 80648]

import_utility.initiate_database()
import_utility.import_tags("tags-20210226.csv", limit=100, my_tags=MY_TAGS)
import_utility.import_fics("works-20210226.csv", limit=100, my_tags=MY_TAGS)

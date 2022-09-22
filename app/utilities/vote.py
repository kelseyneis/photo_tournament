import re


class Vote():
    def __init__(self) -> None:
        pass

    def vote(self, img):
        # TODO: include current user as a parameter and add code to record user's vote
        images = open("images.txt", "r").read().rstrip('\n')
        images_arr = images.split("\n")
        ids = list(map(lambda x: re.search(r"\d+", x).group(), images_arr))
        winning_index = ids.index(img)

        return (images_arr[0], images_arr[1])

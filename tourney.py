images = open("images_for_script.txt", "r").read().rstrip('\n').split('\n')
tournament_round = [i for i in range(len(images) + 1)]


def pairwise(iterable):
    # pairwise code from https://stackoverflow.com/a/5389547
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


while len(tournament_round) > 1:
    next_round = []
    for x, y in pairwise(tournament_round):
        winner = None
        print(f"Choice {x}: {images[x]}")
        print(f"Choice {y}: {images[y]}")
        while winner not in {str(x), str(y)}:
            winner = input(f"Please choose {x} or {y}: ")
        next_round.append(int(winner))
    tournament_round = next_round
print(f"The winner is: {images[int(tournament_round[0])]}")

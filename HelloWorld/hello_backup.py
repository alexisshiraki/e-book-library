score_input = input("Score: ")

try:
    score = int(score_input)
except ValueError:
    print("Please enter an integer score.")
    raise SystemExit(1)

if not (0 <= score <= 100):
    print("Score out of range (0-100).")
else:
    if 90 <= score <= 100:
        print("Grade: A")
    elif 80 <= score < 90:
        print("Grade: B")
    elif 70 <= score < 80:
        print("Grade: C")
    elif 60 <= score < 70:
        print("Grade: D")
    else:
        print("Grade: F")
score_input = input("Score: ")

try:
    score = int(score_input)
except ValueError:
    print("Please enter an integer score.")
    raise SystemExit(1)

if not (0 <= score <= 100):
    print("Score out of range (0-100).")
else:
    if 90 <= score <= 100:
        print("Grade: F")
    elif 70 <= score < 80:
        print("Grade: C")
    elif 60 <= score < 70:
        print("Grade: D")
    else:
        print("Grade: F")

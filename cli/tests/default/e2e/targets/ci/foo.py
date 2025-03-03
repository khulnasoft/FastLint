# Used by test_ci.py

def bar():
    a == a
    a == a
    a == a  # nofastlint
    a == a

    x == x  # nofastlint

    y == y

    z == z  # nofastlint

    x == 5
    y == 5  # nofastlint

    baz == 4  # nofastlint
    baz == 4

    potato == 3

    b == b # Triage ignored by syntactic_id
    a == a # Triage ignored by match_based_id

    d2 = danger
    sink(d2)

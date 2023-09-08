def risk_matrix(risk, impact):
    def convert(number):
        if number == "low":
            number = 1
        elif number == "medium":
            number = 2
        elif number == "high":
            number = 3
        elif number == "critical":
            number = 4
        return number

    risk = convert(risk)
    impact = convert(impact)
    sum = risk * impact

    if sum < 4:
        final_risk = "low"
    elif 5 < sum < 8:
        final_risk = "Medium"
    elif 9 < sum < 12:
        final_risk = "High"
    elif sum == 16:
        final_risk = "Critical"

    # |     low|  Medium|     High|Critical|
    # |       4|       8|       12|      16|Critical
    # |       3|       6|        9|      12|High
    # |       2|       4|        6|       8|Medium
    # |       1|       2|        3|       4|low

    return final_risk


def gpt_summary():
    print("Ey")

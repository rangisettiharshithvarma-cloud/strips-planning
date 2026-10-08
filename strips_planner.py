from dataclasses import dataclass

# ---------------------------
# STRIPS action representation
# ---------------------------
@dataclass(frozen=True)
class Action:
    name: str
    preconditions: frozenset
    add: frozenset
    delete: frozenset


def apply_action(state, action):
    return (state - action.delete) | action.add


def relevant_actions(goal, actions):
    return [a for a in actions if goal in a.add]


def achieve(goal, state, actions, plan):
    """
    Goal-stack style recursion:
    - If goal is already true, done.
    - Otherwise choose a relevant action.
    - Recursively achieve all preconditions.
    - Apply the action.
    """
    if goal in state:
        return state, plan

    options = relevant_actions(goal, actions)
    if not options:
        raise ValueError(f"No action can achieve goal: {goal}")

    for action in options:
        temp_state = set(state)

        # Try to achieve each precondition first
        ok = True
        for pre in action.preconditions:
            if pre not in temp_state:
                try:
                    temp_state, plan = achieve(pre, temp_state, actions, plan)
                except ValueError:
                    ok = False
                    break

        if not ok:
            continue

        new_state = apply_action(temp_state, action)
        plan.append(action.name)
        return new_state, plan

    raise ValueError(f"Goal cannot be achieved: {goal}")


def goal_stack_planner(initial_state, goals, actions):
    state = set(initial_state)
    plan = []

    # goals are processed in order, so the last goal is achieved first
    # (classic stack behavior; this keeps the example simple)
    for goal in list(reversed(goals)):
        state, plan = achieve(goal, state, actions, plan)

    return plan


# ---------------------------
# Example Blocks World problem
# ---------------------------
#
# Initial state:
#   - A is on the table
#   - B is on A
#   - C is on the table
#   - B is clear
#   - C is clear
#
# Goal:
#   - B should be on C
#   - A should be on B
#
# This is a valid plan:
#   move_B_to_C
#   move_A_to_B
#
initial = {
    "on(A, table)",
    "on(B, A)",
    "on(C, table)",
    "clear(B)",
    "clear(C)"
}

goal = {
    "on(B, C)",
    "on(A, B)"
}

actions = [
    Action(
        "move_B_to_C",
        frozenset({"on(B, A)", "clear(B)", "clear(C)"}),
        frozenset({"on(B, C)", "clear(A)"}),
        frozenset({"on(B, A)", "clear(C)"})
    ),
    Action(
        "move_A_to_B",
        frozenset({"on(A, table)", "clear(A)", "clear(B)"}),
        frozenset({"on(A, B)"}),
        frozenset({"on(A, table)", "clear(B)"})
    ),
    Action(
        "move_A_to_table",
        frozenset({"on(A, B)", "clear(A)"}),
        frozenset({"on(A, table)", "clear(B)"}),
        frozenset({"on(A, B)"})
    ),
]

plan = goal_stack_planner(initial, goal, actions)
print("Plan:", plan)

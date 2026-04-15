import gradio as gr

# CISC 121 Final Project -- Playlist Vibe Builder

def validate_playlist(playlist, sort_key):
    # Basic structure checks
    if not isinstance(playlist, list):
        return False, "Playlist must be a list."
    if len(playlist) == 0:
        return False, "Playlist cannot be empty."

    required_fields = ["title", "artist", "energy", "duration"]

    # Validate each song entry
    for i, song in enumerate(playlist):
        if not isinstance(song, dict):
            return False, f"Song at index {i} is not a dictionary."
        for field in required_fields:
            if field not in song:
                return False, f"Song at index {i} is missing required field: '{field}'."
        if sort_key not in song:
            return False, f"Song at index {i} is missing sort key: '{sort_key}'."

        # Validate data types and ranges
        if not isinstance(song["energy"], int) or not (0 <= song["energy"] <= 100):
            return False, f"Song at index {i} must have an energy score between 0 and 100."
        if not isinstance(song["duration"], int) or song["duration"] < 0:
            return False, f"Song at index {i} must have a non-negative duration."

    return True, "Playlist is valid"


def merge_sort_playlist(playlist, sort_key, ascending=True):
    # Validate input before sorting
    is_valid, error_message = validate_playlist(playlist, sort_key)
    if not is_valid:
        raise ValueError(error_message)

    steps = []
    playlist_copy = playlist.copy()

    # Start recursive merge sort
    sorted_playlist = merge_sort_recursive(playlist_copy, sort_key, ascending, steps)
    return sorted_playlist, steps


def merge_sort_recursive(sublist, sort_key, ascending, steps):
    # Base case: already sorted
    if len(sublist) <= 1:
        return sublist

    # Split list into two halves
    mid = len(sublist) // 2
    left_half = sublist[:mid]
    right_half = sublist[mid:]

    steps.append({
        "type": "split",
        "left": left_half[:],
        "right": right_half[:]
    })

    # Recursively sort both halves
    sorted_left = merge_sort_recursive(left_half, sort_key, ascending, steps)
    sorted_right = merge_sort_recursive(right_half, sort_key, ascending, steps)

    # Merge sorted halves
    return merge(sorted_left, sorted_right, sort_key, ascending, steps)


def merge(left, right, sort_key, ascending, steps):
    merged_list = []
    i = 0
    j = 0

    # Compare elements from both lists
    while i < len(left) and j < len(right):
        left_song = left[i]
        right_song = right[j]

        steps.append({
            "type": "compare",
            "left_song": left_song,
            "right_song": right_song
        })

        # Choose ordering direction
        if ascending:
            condition = left_song[sort_key] <= right_song[sort_key]
        else:
            condition = left_song[sort_key] >= right_song[sort_key]

        # Add the correct element to merged list
        if condition:
            merged_list.append(left_song)
            steps.append({
                "type": "place",
                "song": left_song,
                "merged": merged_list[:]
            })
            i += 1
        else:
            merged_list.append(right_song)
            steps.append({
                "type": "place",
                "song": right_song,
                "merged": merged_list[:]
            })
            j += 1

    # Append any remaining elements
    while i < len(left):
        merged_list.append(left[i])
        steps.append({
            "type": "place",
            "song": left[i],
            "merged": merged_list[:]
        })
        i += 1

    while j < len(right):
        merged_list.append(right[j])
        steps.append({
            "type": "place",
            "song": right[j],
            "merged": merged_list[:]
        })
        j += 1

    # Record completed merge
    steps.append({
        "type": "merged section",
        "merged": merged_list[:]
    })

    return merged_list


def format_playlist(playlist):
    # Converts playlist into readable string output 
    lines = []
    for index, song in enumerate(playlist, start=1):
        minutes = song["duration"] // 60
        seconds = song["duration"] % 60
        lines.append(
            f"{index}. {song['title']} - {song['artist']} | "
            f"Energy: {song['energy']} | Duration: {minutes}:{seconds:02d}"
        )
    return "\n".join(lines)

def format_steps(steps):
    # Converts all steps into readable log 
    lines = []
    for step_number, step in enumerate(steps, start=1):
        lines.append(format_single_step(step, step_number, len(steps)))
    return "\n".join(lines)


def format_single_step(step, step_number, total_steps):
    # Formats a single for the interactive display
    if step["type"] == "split":
        left_titles = [song["title"] for song in step["left"]]
        right_titles = [song["title"] for song in step["right"]]
        return f"Step {step_number} of {total_steps}: Split into left {left_titles} and right {right_titles}"

    elif step["type"] == "compare":
        return (
            f"Step {step_number} of {total_steps}: Compare "
            f"'{step['left_song']['title']}' with '{step['right_song']['title']}'"
        )

    elif step["type"] == "place":
        titles = [song["title"] for song in step["merged"]]
        return (
            f"Step {step_number} of {total_steps}: Place '{step['song']['title']}' into merged list. "
            f"Current merged list: {titles}"
        )

    elif step["type"] == "merged section":
        titles = [song["title"] for song in step["merged"]]
        return f"Step {step_number} of {total_steps}: Merged section -> {titles}"

    return f"Step {step_number} of {total_steps}: {step['type']}"


def playlist_to_table(playlist):
    # Converts playlist into a table format for the UI app display 
    rows = []
    for song in playlist:
        minutes = song["duration"] // 60
        seconds = song["duration"] % 60
        rows.append([
            song["title"],
            song["artist"],
            song["energy"],
            f"{minutes}:{seconds:02d}"
        ])
    return rows

def add_song(title, artist, energy, duration, playlist_state):
    # Adds a new song to the playlist with validation
    try:
        title = title.strip()
        artist = artist.strip()

        if title == "":
            return playlist_state, playlist_to_table(playlist_state), "Error: Title cannot be empty.", title_input_default(), artist_input_default(), 50, 180

        if artist == "":
            return playlist_state, playlist_to_table(playlist_state), "Error: Artist cannot be empty.", title, artist, energy, duration

        energy = int(energy)
        duration = int(duration)

        if not (0 <= energy <= 100):
            return playlist_state, playlist_to_table(playlist_state), "Error: Energy must be between 0 and 100.", title, artist, energy, duration

        if duration < 0:
            return playlist_state, playlist_to_table(playlist_state), "Error: Duration must be non-negative.", title, artist, energy, duration

        new_song = {
            "title": title,
            "artist": artist,
            "energy": energy,
            "duration": duration
        }

        updated_playlist = playlist_state + [new_song]

        return updated_playlist, playlist_to_table(updated_playlist), f"Added '{title}' by {artist}.", "", "", 50, 180

    except Exception as e:
        return playlist_state, playlist_to_table(playlist_state), f"Error: {str(e)}", title, artist, energy, duration

def clear_playlist():
    # Reset playlist to empty 
    empty_playlist = []
    return empty_playlist, [], "Playlist cleared."


def sort_playlist_ui(playlist_state, sort_key, order):
    # Handles sorting and prepares the outputs for the UI
    try:
        ascending = (order == "Ascending")
        sorted_playlist, simulation_steps = merge_sort_playlist(
            playlist_state, sort_key, ascending
        )

        if len(simulation_steps) == 0:
            first_step_text = "No steps to display."
            step_counter = "Step 0 of 0"
        else:
            first_step_text = format_single_step(simulation_steps[0], 1, len(simulation_steps))
            step_counter = f"Step 1 of {len(simulation_steps)}"

        return (
            format_playlist(sorted_playlist),
            format_steps(simulation_steps),
            simulation_steps,
            0,
            step_counter,
            first_step_text
        )

    except Exception as e:
        return "", f"Error: {str(e)}", [], 0, "Step 0 of 0", f"Error: {str(e)}"

# All functions used for the interactive step portion
def show_current_step(steps_state, step_index):
    if len(steps_state) == 0:
        return "Step 0 of 0", "No steps to display."

    total_steps = len(steps_state)
    step_text = format_single_step(steps_state[step_index], step_index + 1, total_steps)
    counter_text = f"Step {step_index + 1} of {total_steps}"
    return counter_text, step_text


def next_step(steps_state, step_index):
    if len(steps_state) == 0:
        return step_index, "Step 0 of 0", "No steps to display."

    if step_index < len(steps_state) - 1:
        step_index += 1

    counter_text, step_text = show_current_step(steps_state, step_index)
    return step_index, counter_text, step_text


def previous_step(steps_state, step_index):
    if len(steps_state) == 0:
        return step_index, "Step 0 of 0", "No steps to display."

    if step_index > 0:
        step_index -= 1

    counter_text, step_text = show_current_step(steps_state, step_index)
    return step_index, counter_text, step_text


# Gradio UI Setup Part
example_playlist = []

with gr.Blocks() as demo:
    # App state - Playlist + sorting steps 
    playlist_state = gr.State(example_playlist)
    steps_state = gr.State([])
    step_index_state = gr.State(0)

    gr.Markdown("# CISC 121 - Playlist Vibe Builder")
    gr.Markdown("Add your songs one by one, then sort your playlist using merge sort!")

    # App description / instructions
    with gr.Accordion("How to use this app", open=True):
        gr.Markdown(
            "1. Enter a song title, artist, energy, and duration.\n"
            "2. Click **Add Song**.\n"
            "3. Repeat until your playlist is complete.\n"
            "4. Choose a sort key and sort order.\n"
            "5. Click **Sort Playlist**.\n"
            "6. Use **Previous Step** and **Next Step** to move through and watch the sorting process."
        )

    gr.Markdown("## Add a Song")

    with gr.Row():
        title_input = gr.Textbox(label="Title", placeholder="Enter song title")
        artist_input = gr.Textbox(label="Artist", placeholder="Enter artist name")

    with gr.Row():
        energy_input = gr.Number(label="Energy (0-100)", value=50, precision=0)
        duration_input = gr.Number(label="Duration in seconds", value=180, precision=0)

    with gr.Row():
        add_button = gr.Button("Add Song", variant="primary")
        clear_button = gr.Button("Clear Playlist")

    status_output = gr.Textbox(label="Status", interactive=False)

    gr.Markdown("## Current Playlist")
    playlist_table = gr.Dataframe(
        headers=["Title", "Artist", "Energy", "Duration"],
        value=[],
        row_count=(8, "dynamic"),
        column_count=(4, "fixed"),
        interactive=False,
        wrap=True 
    )

    # Sort keys + sort ordering
    gr.Markdown("## Sort Options")
    with gr.Row():
        sort_key_input = gr.Dropdown(
            choices=["energy", "duration"],
            label="Sort Key",
            value="energy"
        )
        order_input = gr.Radio(
            choices=["Ascending", "Descending"],
            label="Sort Order",
            value="Ascending"
        )

    sort_button = gr.Button("Sort Playlist", variant="primary")

    gr.Markdown("## Sorted Playlist")
    sorted_output = gr.Textbox(lines=10, label="Sorted Playlist")

    gr.Markdown("## Interactive Step Viewer")
    step_counter_output = gr.Textbox(label="Current Step", interactive=False)
    single_step_output = gr.Textbox(lines=8, label="Step Details", interactive=False)

    with gr.Row():
        previous_button = gr.Button("Previous Step")
        next_button = gr.Button("Next Step")

    # Buttons
    gr.Markdown("## Full Step Log")
    all_steps_output = gr.Textbox(lines=12, label="All Simulation Steps")   
    
    add_button.click(
        fn=add_song,
        inputs=[title_input, artist_input, energy_input, duration_input, playlist_state],
        outputs=[
            playlist_state,
            playlist_table,
            status_output,
            title_input,
            artist_input,
            energy_input,
            duration_input
        ]
    )

    clear_button.click(
        fn=clear_playlist,
        inputs=[],
        outputs=[playlist_state, playlist_table, status_output]
    )

    sort_button.click(
        fn=sort_playlist_ui,
        inputs=[playlist_state, sort_key_input, order_input],
        outputs=[
            sorted_output,
            all_steps_output,
            steps_state,
            step_index_state,
            step_counter_output,
            single_step_output
        ]
    )

    next_button.click(
        fn=next_step,
        inputs=[steps_state, step_index_state],
        outputs=[step_index_state, step_counter_output, single_step_output]
    )

    previous_button.click(
        fn=previous_step,
        inputs=[steps_state, step_index_state],
        outputs=[step_index_state, step_counter_output, single_step_output]
    )

demo.launch(share=True)

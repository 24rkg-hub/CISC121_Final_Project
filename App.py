 #CISC 121 Final Project -- Playlist Vibe Builder
def validate_playlist(playlist, sort_key):
  #Validating basic structure
  if not isinstance(playlist, list):
    return False, "Playlist must be a list."
  if len(playlist) == 0:
    return False, "Playlist cannot be empty."
  required_fields = ["title", "artist", "energy", "duration"]

#Validates each song entry 
  for i, song in enumerate(playlist):
    if not isinstance(song, dict):
      return False, f"Song at index {i} is not a dictionary."
    for field in required_fields:
      if field not in song:
        return False, f"Song at index {i} is missing required field: '{field}'."
    if sort_key not in song:
      return False, f"Song at index {i} is missing sort key: '{sort_key}'."
    
    #Validate data types and ranges 
    if not isinstance(song["energy"], int) or not (0 <= song["energy"] <= 100):
      return False, f"Warning: Song at index {i} must have an energy score between 0 and 100."
    if not isinstance(song["duration"], int) or song["duration"] < 0:
      return False, f"Warning: Song at index {i} must have a positive duration."

  return True, "Playlist is valid"

def merge_sort_playlist(playlist, sort_key, ascending=True):
  # Validate input before sorting
  is_valid, error_message = validate_playlist(playlist, sort_key)
  if not is_valid:
    raise ValueError(error_message)

  steps = []
  playlist_copy = playlist.copy()
  #Start the recursive merge sort
  sorted_playlist = merge_sort_recursive(playlist_copy, sort_key, ascending, steps)
  return sorted_playlist, steps

def merge_sort_recursive(sublist, sort_key, ascending, steps):
  # Base case: already sorted 
  if len(sublist) <= 1:
    return sublist

# Split list into the two halves
  mid = len(sublist) // 2
  left_half = sublist[:mid]
  right_half = sublist[mid:]

  steps.append({
      "type": "split",
      "left": left_half[:],
      "right": right_half[:]
  })

# Sort both halves using recursion
  sorted_left = merge_sort_recursive(left_half, sort_key, ascending, steps)
  sorted_right = merge_sort_recursive(right_half, sort_key, ascending, steps)

# Merge the sorted halves
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

# Choose the sorting direction
    if ascending:
      condition = left_song[sort_key] <= right_song[sort_key]

    else:
      condition = left_song[sort_key] >= right_song[sort_key]

# Add the correct element to the merged list
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

# Append any of the remaining elements
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

def print_playlist(playlist):
  # Display playlist in a readable format
  for index, song in enumerate(playlist):
    minutes = song["duration"] // 60
    seconds = song["duration"] % 60
    print(f"{index + 1}. {song['title']} - {song['artist']} | Energy: {song['energy']} | Duration: {minutes}:{seconds:02d}")


def print_steps(steps):
  # Display the step summary
  for step_number, step in enumerate(steps, start=1):
    print(f"Step {step_number}: {step['type']}")

if __name__ == "__main__":
  # Sample test data (DELETE AFTERWARDS)
    playlist = [
        {"title": "Blinding Lights", "artist": "The Weeknd", "energy": 90, "duration": 200},
        {"title": "Someone Like You", "artist": "Adele", "energy": 35, "duration": 285},
        {"title": "Levitating", "artist": "Dua Lipa", "energy": 85, "duration": 203},
        {"title": "Stay", "artist": "The Kid LAROI", "energy": 78, "duration": 141},
        {"title": "drivers license", "artist": "Olivia Rodrigo", "energy": 40, "duration": 242}
    ]


    print("Original Playlist:")
    print_playlist(playlist)

# Run the merge sort
    sorted_playlist, simulation_steps = merge_sort_playlist(playlist, "energy", True)

    print("\nSorted Playlist:")
    print_playlist(sorted_playlist)

    print("\nSimulation Steps:")
    print_steps(simulation_steps)

































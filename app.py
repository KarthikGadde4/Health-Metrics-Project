from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)

# Load norms data from JSON file
with open('data/norms.json', 'r') as file:
    norms_data = json.load(file)

"""
    Find the closest matching age group and norm values for given user metrics.
    
    Args:
        norms_data (dict): Reference data containing norms for different metrics
        user_metrics (dict): User's measured values for different metrics
        gender (str): User's gender
        
    Returns:
        dict: Dictionary containing closest matches for each metric
"""
def find_closest_match(norms_data, user_metrics, gender):
    closest_matches = {}

    for metric, age_groups in norms_data.items():
        closest_matches[metric] = {}

        for age_group, genders in age_groups.items():
            if gender not in genders:
                continue

            norm_values = genders[gender]

            if metric == 'grip_strength':
                left_hand_value = user_metrics.get('grip_strength', {}).get('left_hand', None)
                right_hand_value = user_metrics.get('grip_strength', {}).get('right_hand', None)
                norm_value = norm_values.get('hand')

                # Initialize grip_strength if not already done
                if 'grip_strength' not in closest_matches:
                    closest_matches['grip_strength'] = {}

                if left_hand_value is not None and norm_value is not None:
                    if 'left_hand' not in closest_matches['grip_strength']:
                        closest_matches['grip_strength']['left_hand'] = {}

                    current_closest = closest_matches['grip_strength'].get('left_hand', {})
                    previous_difference = abs(left_hand_value - current_closest.get('norm_value', float('inf')))
                    current_difference = abs(left_hand_value - norm_value)

                    if current_difference < previous_difference:
                        closest_matches['grip_strength']['left_hand'] = {
                            'age_group': age_group,
                            'norm_value': norm_value,
                            'user_value': left_hand_value
                        }

                if right_hand_value is not None and norm_value is not None:
                    if 'right_hand' not in closest_matches['grip_strength']:
                        closest_matches['grip_strength']['right_hand'] = {}

                    current_closest = closest_matches['grip_strength'].get('right_hand', {})
                    previous_difference = abs(right_hand_value - current_closest.get('norm_value', float('inf')))
                    current_difference = abs(right_hand_value - norm_value)

                    if current_difference < previous_difference:
                        closest_matches['grip_strength']['right_hand'] = {
                            'age_group': age_group,
                            'norm_value': norm_value,
                            'user_value': right_hand_value
                        }

            elif metric == 'balance':
                # Initialize balance keys if not already done
                if 'balance' not in closest_matches:
                    closest_matches['balance'] = {}
                
                # Initialize balance subkeys if not already done
                if 'left_open' not in closest_matches['balance']:
                    closest_matches['balance']['left_open'] = {}
                if 'left_closed' not in closest_matches['balance']:
                    closest_matches['balance']['left_closed'] = {}
                if 'right_open' not in closest_matches['balance']:
                    closest_matches['balance']['right_open'] = {}
                if 'right_closed' not in closest_matches['balance']:
                    closest_matches['balance']['right_closed'] = {}

                # Extract user values for balance
                left_open = user_metrics.get('balance', {}).get('left_open', None)
                left_closed = user_metrics.get('balance', {}).get('left_closed', None)
                right_open = user_metrics.get('balance', {}).get('right_open', None)
                right_closed = user_metrics.get('balance', {}).get('right_closed', None)


                # Check if norm values for eyes_open and eyes_closed exist
                eyes_open_norm = norm_values.get('eyes_open', None)
                eyes_closed_norm = norm_values.get('eyes_closed', None)

                # For left_open comparison
                if left_open is not None and eyes_open_norm is not None:
                    current_closest = closest_matches['balance'].get('left_open', {})
                    previous_difference = abs(left_open - current_closest.get('norm_value', float('inf')))
                    current_difference = abs(left_open - eyes_open_norm)

                    if current_difference < previous_difference:
                        closest_matches['balance']['left_open'] = {
                            'age_group': age_group,
                            'norm_value': eyes_open_norm,
                            'user_value': left_open
                        }

                # For left_closed comparison
                if left_closed is not None and eyes_closed_norm is not None:
                    current_closest = closest_matches['balance'].get('left_closed', {})
                    previous_difference = abs(left_closed - current_closest.get('norm_value', float('inf')))
                    current_difference = abs(left_closed - eyes_closed_norm)

                    if current_difference < previous_difference:
                        closest_matches['balance']['left_closed'] = {
                            'age_group': age_group,
                            'norm_value': eyes_closed_norm,
                            'user_value': left_closed
                        }

                # For right_open comparison
                if right_open is not None and eyes_open_norm is not None:
                    current_closest = closest_matches['balance'].get('right_open', {})
                    previous_difference = abs(right_open - current_closest.get('norm_value', float('inf')))
                    current_difference = abs(right_open - eyes_open_norm)

                    if current_difference < previous_difference:
                        closest_matches['balance']['right_open'] = {
                            'age_group': age_group,
                            'norm_value': eyes_open_norm,
                            'user_value': right_open
                        }

                # For right_closed comparison
                if right_closed is not None and eyes_closed_norm is not None:
                    current_closest = closest_matches['balance'].get('right_closed', {})
                    previous_difference = abs(right_closed - current_closest.get('norm_value', float('inf')))
                    current_difference = abs(right_closed - eyes_closed_norm)

                    if current_difference < previous_difference:
                        closest_matches['balance']['right_closed'] = {
                            'age_group': age_group,
                            'norm_value': eyes_closed_norm,
                            'user_value': right_closed
                        }

            elif metric == 'walking_speed':
                if 'walking_speed' not in closest_matches:
                    closest_matches['walking_speed'] = {}
                
                user_speed = user_metrics.get('walking_speed')
                norm_value = norm_values.get('speed')

                if user_speed is not None and norm_value is not None:
                    current_closest = closest_matches['walking_speed']
                    if current_closest.get('user_value') is None or abs(user_speed - norm_value) < abs(user_speed - current_closest.get('norm_value', user_speed)):
                        closest_matches['walking_speed'] = {
                            'age_group': age_group,
                            'norm_value': norm_value,
                            'user_value': user_speed
                         }

    return closest_matches


@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/form-input', methods=['GET'])
def form_input():
    """Render the form input page."""
    return render_template('input.html')

@app.route('/results', methods=['POST'])
def results():
    """Process form submission and display results."""
    try:
        gender = request.form['gender']
        user_metrics = {
            "grip_strength": {
                "right_hand": float(request.form['right_hand_grip']),
                "left_hand": float(request.form['left_hand_grip'])
            },
            "walking_speed": float(request.form['walking_speed']),
            "balance": {
                "left_open": float(request.form['left_open']),
                "left_closed": float(request.form['left_closed']),
                "right_open": float(request.form['right_open']),
                "right_closed": float(request.form['right_closed'])
            }
        }

        # Find closest matches based on user metrics and norms data
        closest_matches = find_closest_match(norms_data, user_metrics, gender)
        
        # Render the results page with the closest matches data
        return render_template('results.html', closest_matches=closest_matches)

    except Exception as e:
        return f"An error occurred: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)

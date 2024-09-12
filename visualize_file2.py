import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from yaml import safe_load

# Global configurations
block_width = 1.5
block_height = 1.5
colors = {
  'event': 'orange',
  'view': '#9acd32',
  'command': '#00bfff',
  'ui': '#d3d3d3',
  'processor': '#9932CC'
}
already_drawn = set()
x, y = 0, 0
y_positions = {}

def offset_x(modifier=0.5):
    global x
    x += block_width * modifier

def offset_y(modifier=2):
    global y
    y += block_width * modifier

def add_y_position(block: str):
    global y
    y_positions[block] = y

# Add blocks and elements
def add_block(id, x, y, color, text):
    id += '_block'
    if id in already_drawn:
        return
    already_drawn.add(id)
    ax.add_patch(
        Rectangle(
            (x, y - block_height / 2),
            block_width,
            block_height,
            color=color
        )
    )
    ax.text(x + block_width / 2, y, text, ha='center', va='center', fontsize=8, color='black')

def identity_property(id, x, y, text):
    id += '_identity_property'
    if id in already_drawn:
        return
    already_drawn.add(id)
    ax.text(
        x, y, text,
        ha='center',
        va='center',
        fontsize=8,
        color='black'
    )

def trigger_identity_property(trigger):
    identity_property(
        trigger['id'],
        x + block_width / 2,
        y_positions[trigger['role']] + block_height * 0.75,
        trigger['identity_property']
    )

def event_identity_property(event):
    identity_property(
        event['id'],
        x + block_width / 2,
        y_positions[event['service']] - block_height * 0.75,
        event['identity_property'],
    )

def ui_block():
    trigger_identity_property(slice['trigger'])
    add_block(
        slice['trigger']['id'],
        x, y_positions[slice['trigger']['role']],
        colors['ui'],
        slice['trigger']['name']
    )

def command_view_block(type):
    add_block(
        slice[type]['id'],
        x, y_positions['command_view'],
        colors[type],
        slice[type]['name']
    )

def event_block(event):
    add_block(
        event['id'],
        x, y_positions[event['service']],
        colors['event'],
        event['name']
    )
    event_identity_property(event)

def processor_block():
    y = y_positions['processor']
    text = slice['processor']['name']
    ax.text(x, y, '⚙️', ha='center', va='center', fontsize=32, color='black')
    ax.text(x, y + block_height, text, ha='center', va='center', fontsize=8, color='black')

def down_arrow(start_x, start_y, end_x, end_y):
    ax.add_patch(
        FancyArrowPatch(
            (start_x + block_width * 0.75, start_y - block_height * 0.5),
            (end_x + block_width * 0.75, end_y + block_height * 0.5),
            mutation_scale=8
        )
    )

def up_arrow(start_x, start_y, end_x, end_y):
    ax.add_patch(
        FancyArrowPatch(
            (start_x + block_width * 0.25, start_y + block_height * 0.5),
            (end_x + block_width * 0.75, end_y - block_height * 0.5),
            mutation_scale=8
        )
    )

# Command pattern
def command_pattern():
    if slice['trigger']['id'] in already_drawn:
        down_arrow(
            x - block_width * 0.5, y_positions[slice['trigger']['role']],
            x, y_positions['command_view']
        )
    else:
        ui_block()
        down_arrow(
            x, y_positions[slice['trigger']['role']],
            x, y_positions['command_view']
        )
    offset_x()
    command_view_block('command')
    down_arrow(
        x, y_positions['command_view'],
        x, y_positions[slice['event']['service']]
    )
    offset_x()
    event_block(slice['event'])

# View pattern
def view_pattern():
    event_block(slice['event'])
    up_arrow(
        x, y_positions[slice['event']['service']],
        x, y_positions['command_view']
    )
    offset_x()
    command_view_block('view')
    up_arrow(
        x, y_positions['command_view'],
        x, y_positions[slice['trigger']['role']]
    )
    offset_x()
    ui_block()

# Automation pattern
def automation_pattern():
    event_block(slice['events'][0])
    up_arrow(
        x, y_positions[slice['events'][0]['service']],
        x, y_positions['command_view']
    )
    offset_x()
    command_view_block('view')
    up_arrow(
        x, y_positions['command_view'],
        x, y_positions['processor']
    )
    offset_x(modifier=1)
    processor_block()
    down_arrow(
        x - block_width * 0.5, y_positions['processor'],
        x, y_positions['command_view']
    )
    offset_x()
    command_view_block('command')
    down_arrow(
        x, y_positions['command_view'],
        x, y_positions[slice['events'][1]['service']]
    )
    offset_x()
    event_block(slice['events'][1])

# Translation pattern
def translation_pattern():
    automation_pattern()

# Function to visualize YAML file
def visualize_yml(file_name="data/temp.yml"):
    global ax, slice
    
    # read data
    data = safe_load(open(file_name))
    slices = data['process']['slices']
    services = list(reversed(data['services']))
    roles = list(reversed(data['roles']))

    # make sure not to draw duplicates
    global already_drawn
    already_drawn = set()

    # setup the figure
    fig, ax = plt.subplots()
    fig.suptitle(data['process']['name'])

    # axes functions
    global x, y
    x, y = 0, 0
    global y_positions
    y_positions = {}

    # define y-positions
    labels = services + ['command_view', 'processor'] + roles
    for label in labels:
        add_y_position(label)
        offset_y()

    # add patterns
    for slice in slices:
        if slice['pattern'] == 'Command':
            command_pattern()
        elif slice['pattern'] == 'View':
            view_pattern()
        elif slice['pattern'] == 'Automation':
            automation_pattern()
        elif slice['pattern'] == 'Translation':
            translation_pattern()
        else:
            raise Exception(f'No such pattern: {slice["pattern"]}')
        offset_x()

    # add swimlanes
    for label, y in y_positions.items():
        if not (label == 'command_view' or label == 'processor'):
            ax.text(-1, y, label, va='center', ha='right', fontsize=12, fontweight='bold')
            ax.add_patch(
                Rectangle(
                    (0, y - block_height / 2),
                    width=x + block_width / 2,
                    height=block_height,
                    fill=False,
                    edgecolor='black'
                )
            )

    # set limits and remove axes
    ax.set_xlim(-block_width, block_width * 16)
    ax.set_ylim(-block_height, y + block_height)
    ax.axis('off')

    # show the plot
    plt.show()

if __name__ == '__main__':
    visualize_yml(file_name="data/temp.yml")

from fasthtml.components import Div, H1, Title
from fasthtml.core import FastHTML, serve
import matplotlib.pyplot as plt
import pandas as pd

# Import QueryBase, Employee, Team from employee_events
from employee_events import Employee, Team
# import the load_model function from the utils.py file
from utils import load_model
# Below, we import the parent classes
# you will use for subclassing
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, entity_id, model):
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name
        
        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model)
    
    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(self, entity_id, model):
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        return model.names()

# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    def component_data(self, entity_id, model):
        return None

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(self, entity_id, model):

        label = model.name.title()

        # Show the selected entity in the page title, e.g. "Employee: Fiona Sullivan".
        selected = None
        if entity_id is not None and hasattr(model, 'username'):
            result = model.username(entity_id)
            if result and result[0]:
                selected = result[0][0]

        if selected:
            return H1(f"{label}: {selected}")

        return H1(label)

# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):

    def component_data(self, entity_id, model):
        return None
    
    # Overwrite the parent class's `visualization`
    # method. Use the same parameters as the parent
    def visualization(self, entity_id, model):

        # Pass the `entity_id` argument to
        # the model's `event_counts` method to
        # receive the x (Day) and y (event count)
        x = model.event_counts(entity_id).copy()

        # Some teams have no historical events. Render a zero-state chart
        # instead of raising when pandas receives no numeric data.
        if x.empty:
            _, ax = plt.subplots()
            self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
            ax.set_title('Cumulative Event Counts', fontsize=20)
            ax.set_xlabel('Date', fontsize=15)
            ax.set_ylabel('Event Count', fontsize=15)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.text(0.5, 0.5, 'No event data available', ha='center', va='center', transform=ax.transAxes)
            return

        x[['positive_events', 'negative_events']] = x[['positive_events', 'negative_events']].apply(
            pd.to_numeric,
            errors='coerce',
        ).fillna(0)

        # Use the pandas .fillna method to fill nulls with 0
        x.fillna(0, inplace=True)        
        # User the pandas .set_index method to set
        # the date column as the index
        x.set_index('event_date', inplace=True)
        
        # Sort the index
        x.sort_index(inplace=True)
        
        # Use the .cumsum method to change the data
        # in the dataframe to cumulative counts
        x = x.cumsum()
        
        # Set the dataframe columns to the list
        # ['Positive', 'Negative']
        x.columns = ['Positive', 'Negative']
        
        # Initialize a pandas subplot
        # and assign the figure and axis
        # to variables
        _, ax = plt.subplots()
        
        # call the .plot method for the
        # cumulative counts dataframe
        x.plot(ax=ax)
        
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        # Use keyword arguments to set 
        # the border color and font color to black. 
        # Reference the base_components/matplotlib_viz file 
        # to inspect the supported keyword arguments
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')        
        # Set title and labels for x and y axis
        ax.set_title('Cumulative Event Counts', fontsize=20)
        ax.set_xlabel('Date', fontsize=15)
        ax.set_ylabel('Event Count', fontsize=15)


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):
    # Create a `predictor` class attribute
    # assign the attribute to the output
    # of the `load_model` utils function
    predictor = load_model()
    def component_data(self, entity_id, model):
        return None

    # Overwrite the parent class `visualization` method
    # Use the same parameters as the parent
    def visualization(self, entity_id, model):

        # Using the model and entity_id arguments
        # pass the `entity_id` to the `.model_data` method
        # to receive the data that can be passed to the machine
        # learning model
        data = model.model_data(entity_id).copy()

        if data.empty:
            pred = 0
        else:
            data = data.apply(pd.to_numeric, errors='coerce').fillna(0)
        # Using the predictor class attribute
        # pass the data to the `predict_proba` method
            proba = self.predictor.predict_proba(data)
            
            # Index the second column of predict_proba output
            # The shape should be (<number of records>, 1)
            proba = proba[:, 1]
            
            
            # Below, create a `pred` variable set to
            # the number we want to visualize
            #
            # If the model's name attribute is "team"
            # We want to visualize the mean of the predict_proba output
            if model.name == "team":
                pred = proba.mean()

                
            # Otherwise set `pred` to the first value
            # of the predict_proba output
            else:
                pred = proba[0]
        
        # Initialize a matplotlib subplot
        _, ax = plt.subplots()
        
        # Run the following code unchanged
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        if data.empty:
            ax.text(0.5, 0.5, 'No model data available', ha='center', va='center', transform=ax.transAxes)
        
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
 
# Create a subclass of combined_components/CombinedComponent
# called Visualizations       
class Visualizations(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    children = [LineChart(), BarChart()]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')
            
# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):
    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(self, entity_id, model):
        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes 
        # method. Return the output
        return model.notes(entity_id)
    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    
# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):
    # Set the `children`
    # class attribute to a list
    # containing initialized instances 
    # of the header, dashboard filters,
    # data visualizations, and notes table
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


# Initialize a fasthtml app 
app = FastHTML()
# Initialize the `Report` class
report = Report()


app.title = "Dashboard"

# Create a route for a get request
# Set the route's path to the root
@app.get('/')
def root():
    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return Title("Employee"), report(1, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`. 
# parameterize the employee ID 
# to a string datatype
@app.get('/employee/{employee_id}')
def get_employee(employee_id: str):

    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return Title("Employee"), report(employee_id, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`. 
# parameterize the team ID 
# to a string datatype
@app.get('/team/{team_id}')
def get_team(team_id: str):
    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    return Title("Team"), report(team_id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown')
def update_dropdown(profile_type: str):
    dropdown = DashboardFilters.children[1]
    print('PARAM', profile_type)
    if profile_type == 'Team':
        return dropdown(None, Team())
    elif profile_type == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data.get('profile_type')
    selection_id = data.get('user-selection')
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{selection_id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{selection_id}", status_code=303)
    


serve()

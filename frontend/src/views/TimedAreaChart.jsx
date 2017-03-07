import {d3} from 'd3';
import {AreaChart} from 'react-d3-basic';

import React from 'react'
import HeaderView from './HeaderView.jsx'
import LoadingView from './LoadingView.jsx'
import { Navbar, Nav, NavDropdown, NavItem, MenuItem, Col } from 'react-bootstrap';
import {connect} from 'react-redux';

class TimedAreaChart extends React.Component {
    render() {
        const {chartData} = this.props;

        let width = 700,
            height = 300,
            chartSeries = [
                {
                    field: 'time_footprint',
                    name: 'Task Execution Footprint (seconds)',
                    color: 'orange',
                    style: {
                        opacity: .3
                    }
                }
            ],
            // your x accessor
            x = function(d) {
                return new Date(parseFloat(d.time) * 1000);
            },
            xScale = 'time',
            yTickOrient = 'right';

        return <AreaChart
                  data= {chartData}
                  width= {width}
                  height= {height}
                  chartSeries= {chartSeries}
                  x= {x}
                  xScale= {xScale}
                  yTickOrient= {yTickOrient}
               />
    }
}


TimedAreaChart.contextTypes = {
    store: React.PropTypes.object
};

export default TimedAreaChart = connect(
    (state) => {
        return {
            items: state.jobDoneStats || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(TimedAreaChart);

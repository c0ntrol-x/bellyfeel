import  '../styles/app.less'

import React from 'react'
import {render} from 'react-dom'
import {Provider} from 'react-redux'
import {createStore, compose} from 'redux'
import {CanaryDocsReactApplication} from './reducers.jsx'

// First we import some components...
import { Router, Route } from 'react-router'
import {loadState, saveState, clearState} from './models.jsx'
import HeaderView from './views/HeaderView.jsx'
import DashboardView from './views/DashboardView.jsx'
import ProjectDetailView from './views/ProjectDetailView.jsx'
import BuildDetailView from './views/BuildDetailView.jsx'
import ProjectCreateView from './views/ProjectCreateView.jsx'
import history from './core.jsx'

import $ from 'jquery'

$(function(){
    let store = createStore(CanaryDocsReactApplication, loadState(), compose(
        window.devToolsExtension ? window.devToolsExtension() : f => f
    ));

    render((<Provider store={store}>
    <Router history={history}>
        <Route path="/" component={DashboardView} />
        <Route path="/project/:project_id" component={ProjectDetailView} />
        <Route path="/build/:build_id" component={BuildDetailView} />
    </Router>
    </Provider>), document.getElementById('app-container'))
})

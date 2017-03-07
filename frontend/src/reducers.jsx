import {_} from 'lodash'
import cookie from 'react-cookie';

export const CanaryDocsReactApplication = (state, action) => {
    const user_token = cookie.load('bellyfeel_token');
    switch (action.type) {
        case "LIST_PROJECTS":
            return {...state, projects: action.projects}
            break;
        case "LIST_REPOS":
            return {...state, repos: action.repos}
            break;
        case "LIST_BUILDS":
            return {...state, builds: action.builds}
            break;
        case "PROJECT_DETAILS":
            return {...state, currentProject: action.project}
            break;
        case "BUILD_DETAILS":
            return {...state, currentBuild: action.build}
            break;
        case "BUILD_DELETED":
            let filtered = state.builds.filter((build, i) => {
                return build.id !== action.build_id
            });
            return {...state, currentBuild: null, builds: filtered}
            break;
        case "CLEAR_ERRORS":
            return {...state, errors: []}
            break;
        case "ERROR":
            let errors = [...state.errors || [], {"message": action.message}];
            console.log(errors)
            return {...state, errors: errors}
            break;
        default:
            return {...state, user_token: user_token};
            break;
    }
}

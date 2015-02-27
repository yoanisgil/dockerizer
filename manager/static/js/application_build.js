/**
 * Created by brujitos on 15-02-26.
 */

// For any third party dependencies, like jQuery, place them in the lib folder.

// Configure loading modules from the lib directory,
// except for 'app' ones, which are in a sibling
// directory.
requirejs.config({
    paths: {
        app: '../application_build'
    }
});

// Start loading the main app file. Put all of
// your application logic in there.
requirejs(['application_build/main']);

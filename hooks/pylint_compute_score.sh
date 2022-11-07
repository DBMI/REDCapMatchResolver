pylint .\\src\\REDCapReportWriter\\ | sed --quiet 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p'

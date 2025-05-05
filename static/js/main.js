/**
 * Karmayogi Bharat - Learning Path Recommender
 * Advanced JavaScript functionality for interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.main-navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Initialize tooltips and popovers
    if (typeof bootstrap !== 'undefined') {
        // Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.forEach(function (popoverTriggerEl) {
            new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Form validation and enhanced UI for select inputs
    const selectInputs = document.querySelectorAll('.form-select');
    selectInputs.forEach(select => {
        select.addEventListener('change', function() {
            if (this.value) {
                this.classList.add('is-valid');
                this.parentElement.classList.add('is-valid-parent');
            } else {
                this.classList.remove('is-valid');
                this.parentElement.classList.remove('is-valid-parent');
            }
        });
    });

    // Form submission with validation and loading animation
    const recommendationForm = document.getElementById('recommendation-form');
    if (recommendationForm) {
        recommendationForm.addEventListener('submit', function(event) {
            const designation = document.getElementById('designation').value;
            const ministry = document.getElementById('ministry').value;
            
            if (!designation || !ministry) {
                event.preventDefault();
                
                // Show error message with animation
                const errorMessage = document.createElement('div');
                errorMessage.className = 'alert alert-danger animate__animated animate__shakeX';
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Please select both designation and ministry';
                
                // Remove any existing error messages
                const existingErrors = document.querySelectorAll('.alert-danger');
                existingErrors.forEach(el => el.remove());
                
                // Insert the error message after the form heading
                const formHeading = recommendationForm.querySelector('.lead');
                formHeading.insertAdjacentElement('afterend', errorMessage);
                
                // Highlight empty fields
                if (!designation) {
                    document.getElementById('designation').classList.add('is-invalid');
                }
                if (!ministry) {
                    document.getElementById('ministry').classList.add('is-invalid');
                }
                
                // Scroll to form
                recommendationForm.scrollIntoView({ behavior: 'smooth' });
                
                // Remove error message after 5 seconds
                setTimeout(() => {
                    errorMessage.classList.add('animate__fadeOut');
                    setTimeout(() => errorMessage.remove(), 500);
                }, 5000);
            } else {
                // Add loading animation
                const button = this.querySelector('button[type="submit"]');
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Generating...';
                button.disabled = true;
                
                // Add animation to the form
                this.closest('.card').classList.add('generating');
            }
        });
    }

    // Handle API form submission if it exists (for single-page version)
    const apiForm = document.getElementById('api-recommendation-form');
    if (apiForm) {
        apiForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const designation = document.getElementById('designation').value;
            const ministry = document.getElementById('ministry').value;
            
            if (!designation || !ministry) {
                // Show error using toast or alert
                showNotification('Please select both designation and ministry', 'error');
                return;
            }
            
            // Show loading animation
            showLoadingState(true);
            
            // Make API request
            fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    designation: designation,
                    ministry: ministry
                }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Hide loading and show results
                showLoadingState(false);
                
                // Display results with animations
                displayResults(data);
                showNotification('Learning path generated successfully!', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showLoadingState(false);
                showNotification('An error occurred while fetching recommendations.', 'error');
            });
        });
    }
    
    // Toggle course details in the recommendations page
    const toggleButtons = document.querySelectorAll('.toggle-course-details');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const detailsElement = document.getElementById('courseDetails' + courseId);
            
            if (detailsElement.classList.contains('show')) {
                detailsElement.classList.remove('show');
                this.querySelector('i').classList.remove('fa-chevron-up');
                this.querySelector('i').classList.add('fa-chevron-down');
            } else {
                detailsElement.classList.add('show');
                this.querySelector('i').classList.remove('fa-chevron-down');
                this.querySelector('i').classList.add('fa-chevron-up');
            }
        });
    });
    
    // Expand/collapse all course details
    const expandAllBtn = document.getElementById('expandAllBtn');
    const collapseAllBtn = document.getElementById('collapseAllBtn');
    
    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', function() {
            document.querySelectorAll('.course-details').forEach(el => {
                el.classList.add('show');
            });
            document.querySelectorAll('.toggle-course-details i').forEach(icon => {
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            });
        });
    }
    
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', function() {
            document.querySelectorAll('.course-details').forEach(el => {
                el.classList.remove('show');
            });
            document.querySelectorAll('.toggle-course-details i').forEach(icon => {
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            });
        });
    }
    
    // Function to show loading state
    function showLoadingState(isLoading) {
        const loadingIndicator = document.getElementById('loading-indicator');
        const resultsContainer = document.getElementById('results-container');
        
        if (loadingIndicator && resultsContainer) {
            if (isLoading) {
                loadingIndicator.classList.remove('d-none');
                resultsContainer.classList.add('d-none');
            } else {
                loadingIndicator.classList.add('d-none');
                resultsContainer.classList.remove('d-none');
            }
        }
    }
    
    // Function to show notification/toast
    function showNotification(message, type) {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '1050';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'error' ? 'bg-danger' : 'bg-success';
        const icon = type === 'error' ? 'exclamation-circle' : 'check-circle';
        
        const toastHtml = `
            <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
                <div class="toast-header ${bgClass} text-white">
                    <i class="fas fa-${icon} me-2"></i>
                    <strong class="me-auto">${type === 'error' ? 'Error' : 'Success'}</strong>
                    <small>just now</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Initialize and show toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
            
            // Remove toast from DOM after it's hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        }
    }
    
    // Function to display API results on the page
    function displayResults(data) {
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer) return;
        
        // Create competency section
        const competenciesContainer = document.getElementById('competencies-container');
        if (competenciesContainer && data.competencies) {
            let behavioralHtml = '';
            let functionalHtml = '';
            let domainHtml = '';
            
            data.competencies.forEach(comp => {
                const item = `
                    <div class="competency-item p-3" data-aos="fade-up">
                        <div class="competency-name">${comp.name}</div>
                        <div class="competency-description">${comp.description}</div>
                    </div>
                `;
                
                if (comp.type === 'Behavioral') {
                    behavioralHtml += item;
                } else if (comp.type === 'Functional') {
                    functionalHtml += item;
                } else if (comp.type === 'Domain') {
                    domainHtml += item;
                }
            });
            
            const behavioralList = document.getElementById('behavioral-list');
            const functionalList = document.getElementById('functional-list');
            const domainList = document.getElementById('domain-list');
            
            if (behavioralList) {
                behavioralList.innerHTML = behavioralHtml || 
                    '<div class="competency-item p-3 text-center"><div class="competency-name text-muted">No behavioral competencies</div></div>';
            }
            
            if (functionalList) {
                functionalList.innerHTML = functionalHtml || 
                    '<div class="competency-item p-3 text-center"><div class="competency-name text-muted">No functional competencies</div></div>';
            }
            
            if (domainList) {
                domainList.innerHTML = domainHtml || 
                    '<div class="competency-item p-3 text-center"><div class="competency-name text-muted">No domain competencies</div></div>';
            }
        }
        
        // Create learning path section
        const learningPathContainer = document.getElementById('learning-path-container');
        if (learningPathContainer && data.learning_path) {
            let pathHtml = '';
            
            data.learning_path.forEach((course, index) => {
                // Badge styling based on level
                let levelBadgeClass = 'badge-intermediate';
                let levelIcon = 'user';
                
                if (course.level === 'Beginner') {
                    levelBadgeClass = 'badge-beginner';
                    levelIcon = 'seedling';
                } else if (course.level === 'Advanced') {
                    levelBadgeClass = 'badge-advanced';
                    levelIcon = 'star';
                }
                
                pathHtml += `
                    <div class="course-card mb-4" data-aos="fade-up" data-aos-delay="${150 + (index * 50)}">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <div class="d-flex">
                                    <div class="timeline-badge me-3">
                                        <span class="fs-4">${course.order}</span>
                                    </div>
                                    <div class="flex-grow-1">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <h4 class="card-title mb-0">${course.title}</h4>
                                            <button class="btn btn-sm btn-link toggle-course-details" data-course-id="${course.id}">
                                                <i class="fas fa-chevron-down"></i>
                                            </button>
                                        </div>
                                        
                                        <div class="course-summary mb-3">
                                            <div class="d-flex flex-wrap course-meta">
                                                <span class="badge me-2 mb-2">
                                                    <i class="fas fa-building me-1"></i> ${course.provider}
                                                </span>
                                                <span class="badge me-2 mb-2">
                                                    <i class="fas fa-layer-group me-1"></i> ${course.domain}
                                                </span>
                                                <span class="badge me-2 mb-2">
                                                    <i class="fas fa-clock me-1"></i> ${course.duration_hours} hrs
                                                </span>
                                                <span class="badge ${levelBadgeClass} me-2 mb-2">
                                                    <i class="fas fa-${levelIcon} me-1"></i> ${course.level}
                                                </span>
                                                <span class="badge me-2 mb-2">
                                                    <i class="fas fa-laptop me-1"></i> ${course.course_type}
                                                </span>
                                            </div>
                                        </div>
                                        
                                        <div class="course-details collapse" id="courseDetails${course.id}">
                                            <div class="course-description mb-3">
                                                <p>${course.description}</p>
                                            </div>
                                            
                                            <div class="course-actions mt-3">
                                                <button class="btn btn-sm btn-primary">
                                                    <i class="fas fa-external-link-alt me-1"></i> Enroll in Course
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            learningPathContainer.innerHTML = pathHtml || 
                '<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>No course recommendations available for this role.</div>';
                
            // Re-initialize the toggle buttons
            setTimeout(() => {
                const newToggleButtons = learningPathContainer.querySelectorAll('.toggle-course-details');
                newToggleButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const courseId = this.getAttribute('data-course-id');
                        const detailsElement = document.getElementById('courseDetails' + courseId);
                        
                        if (detailsElement.classList.contains('show')) {
                            detailsElement.classList.remove('show');
                            this.querySelector('i').classList.remove('fa-chevron-up');
                            this.querySelector('i').classList.add('fa-chevron-down');
                        } else {
                            detailsElement.classList.add('show');
                            this.querySelector('i').classList.remove('fa-chevron-down');
                            this.querySelector('i').classList.add('fa-chevron-up');
                        }
                    });
                });
            }, 100);
        }
        
        // Reinitialize AOS for newly added elements
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
    }
});

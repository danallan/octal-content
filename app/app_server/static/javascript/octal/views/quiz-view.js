define(["backbone", "underscore", "jquery", "octal/utils/utils"], function(Backbone, _, $, Utils){

		
		var QuizView = (function() {
				var pvt = {};
				pvt.viewConsts = {
						templateId: "quiz-view-template",
						viewId: "quiz"
				};
				pvt.isRendered = false;
				
				
				return Backbone.View.extend({

						template: _.template(document.getElementById( pvt.viewConsts.templateId).innerHTML),

						tagName:  'div',

						// Cache the template function for a single item.
						todoTpl: _.template( "An example template" ),
						
						isRendered: function(){
								return pvt.isRendered;
						},

						events: {
								'dblclick label': 'edit',
								'keypress .edit': 'updateOnEnter',
								'blur .edit':   'close',
								'click .submit-button': 'submit'
						},

						// Re-render the title of the todo item.
						render: function() {
								var thisView = this;
								var thisModel = thisView.model;
								var h = _.clone(thisModel.toJSON());
								
								thisView.$el.html(thisView.template(h));
								$('#header').remove();
								$('#apptools').remove();
								
								pvt.isRendered = true;
								return this;
						},

						//If no button selected, returns undefined
						submit: function() {
							  console.log($("input[type='radio'][name='answer']:checked").val());
								//TODO: build model to submit, actually submit to server
						},
						edit: function() {
								// executed when todo label is double clicked
						},

						close: function() {
								// executed when todo loses focus
						},

						updateOnEnter: function( e ) {
								// executed on each keypress when in todo edit mode,
								// but we'll wait for enter to get in action
						}
						

				});
		})();

		var quizView = new QuizView();

		// log reference to a DOM element that corresponds to the view instance

		return QuizView;
});

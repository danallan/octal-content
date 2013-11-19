
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
            
						
						isRendered: function(){
								return pvt.isRendered;
						},

						events: {
								'click .submit-button': 'submit'
						},

						// Re-render the title of the todo item.
						render: function() {
								var thisView = this;
								var thisModel = thisView.model;
								thisModel.set("concept",thisModel.get("concept").replace(/_/g, " "));
								var h = _.clone(thisModel.toJSON());
								
								thisView.$el.html(thisView.template(h));
							  
								
								pvt.isRendered = true;
								return this;
						},

						//If no button selected, returns undefined
						submit: function() {
							  console.log($("input[type='radio'][name='answer']:checked").val());
								//TODO: build model to submit, actually submit to server
						},
						edit: function() {
								
						},

						close: function() {
								//$('#header').css('display', 'block');
						},
						

				});
		})();

		var quizView = new QuizView();

		// log reference to a DOM element that corresponds to the view instance

		return QuizView;
});

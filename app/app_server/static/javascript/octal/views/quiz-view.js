
define(["backbone", "underscore", "jquery", "octal/utils/utils", "octal/models/quiz-model"], function(Backbone, _, $, Utils, QuestionModel){

		var shuffle = function(array) {
				for(var j, x, i = array.length; i; j = Math.floor(Math.random() * i), x = array[--i], array[i] = array[j], array[j] = x);
				return array;
		}
		
		var QuizView = (function() {
				var pvt = {};
				pvt.viewConsts = {
						templateId: "quiz-view-template",
						viewId: "quiz",
				};
				pvt.isRendered = false;

				var ans = "";
				
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
								var thiseView = thisView.options.appRouter.eview;
								thisView.$el.empty();
								//var eView = thisRoute.eview;
								thisModel.set("concept",thisModel.get("concept").replace(/_/g, " "));
								ans = thisModel.get("a")[0];
								thisModel.set("a", shuffle(thisModel.get("a")));
								//thisModel.set("eview", thiseView.el.outerHTML);
								var h = _.clone(thisModel.toJSON());
								thisView.$el.html(thisView.template(h));
							  thisView.$el.find('#graph-wrapper').append(thisView.options.appRouter.eview.el);
								pvt.isRendered = true;
								return this;
						},

						//If no button selected, returns undefined
						submit: function() {
							  var attempt = $("input[type='radio'][name='answer']:checked").val();
								console.log(ans);
								if(ans == attempt)
										alert('nice');
								else
										alert('you fucked up');
								//get new model from the server
								this.model = new QuestionModel({concept: window.location.href.split('/').pop().split('#').shift()});
								//rerender the view TODO: seems kinda wasteful to totally rerender the view rather than the question
								this.render();
						},
						displayNextQuestion: function() {
								var thisView = this;
								render();
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
